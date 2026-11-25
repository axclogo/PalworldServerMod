-- UE4SS boundary tests, run with Lua 5.4 from the project root.
-- These mocks verify our event handling, not Unreal ABI or native game behavior.
local count = 0
local function test(name, body)
    body()
    count = count + 1
    print("PASS " .. name)
end

local function remote(value)
    return {get = function() return value end}
end

local function object(fields)
    fields = fields or {}
    fields.IsValid = function(self) return self.valid ~= false end
    return fields
end

local function load_mod(path, extra)
    local env = extra or {}
    env.hooks = {}
    env.print = env.print or function() end -- Keep routine startup messages out of the test output.
    env.RegisterHook = function(name, pre, post)
        env.hooks[name] = {pre = pre, post = post}
    end
    setmetatable(env, {__index = _G})
    if arg[1] then
        local side, member = path:match("^mods/(%a+)/(.+)$")
        path = arg[1] .. "/" .. side .. "/Mods/" .. member
    end
    assert(loadfile(path, "t", env))()
    return env
end

local function load_fishing(entries)
    local messages = {}
    local env = load_mod("mods/client/PalFishingWin/Scripts/main.lua", {
        StaticFindObject = function(path)
            assert(path == "/Script/Pal.EPalFishingRodState")
            return object({valid = entries ~= nil, ForEachName = function(_, visit)
                for _, entry in ipairs(entries) do
                    if visit({ToString = function() return entry[1] end}, entry[2]) then break end
                end
            end})
        end,
        print = function(message) messages[#messages + 1] = message end,
    })
    return env, messages
end

local function fishing(wait_hit)
    local env = load_fishing({{"EPalFishingRodState::WaitHit", wait_hit or 6}})
    local name, hook = next(env.hooks)
    assert(name == "/Script/Pal.PalFishingComponent:OnChangeRodState" and next(env.hooks, name) == nil)
    assert(hook.pre and not hook.post)
    local controller = object({local_player = true})
    function controller:IsLocalPlayerController() return self.local_player end
    local character = object()
    function character:IsA(class) return class == "/Script/Pal.PalPlayerCharacter" end
    function character:GetPalPlayerController() return controller end
    local rod = object({held = false, presses = 0})
    function rod:GetOwner() return character end
    function rod:IsFishingButtonPressed() return self.held end
    function rod:OnPressedFishingButton() self.presses, self.held = self.presses + 1, true end
    return hook.pre, rod, controller
end

test("fishing uses one rod hook to press the local player's fishing button", function()
    local hook, rod = fishing()
    hook(remote(rod), remote(6))
    assert(rod.presses == 1 and rod.held)
end)

test("fishing skips other rod states, another player's bite and an already held button", function()
    local hook, rod, controller = fishing()
    hook(nil, remote(7)) -- A transition outside WaitHit must not read its rod.
    controller.local_player = false
    hook(remote(rod), remote(6))
    controller.local_player, rod.held = true, true
    hook(remote(rod), remote(6))
    assert(rod.presses == 0)
end)

test("fishing follows the reflected bite value and skips a missing state", function()
    local hook, rod = fishing(12)
    hook(remote(rod), remote(6))
    assert(rod.presses == 0)
    hook(remote(rod), remote(12))
    assert(rod.presses == 1)
    for _, entries in ipairs({false, {{"EPalFishingRodState::CatchBattle", 6}}}) do
        local env, messages = load_fishing(entries or nil)
        assert(next(env.hooks) == nil and #messages == 1 and messages[1]:find("WaitHit missing", 1, true))
    end
end)

local function map_scene()
    local s = {scans = 0, writes = 0, bodies = {}}
    local dead = object({valid = false})
    local world = object()
    local function image()
        return object({visibility = 0, IsA = function(_, class) return class == "/Script/UMG.Image" end,
            GetVisibility = function(self) return self.visibility end,
            SetVisibility = function(self, v) assert(v == 2); self.visibility = v; s.writes = s.writes + 1 end})
    end
    function s.body(template)
        local b = object({Image_MapMask = image(), WidgetTree = object(), Cloud = image(), Icons = image(),
            HasAnyFlags = function(_, flags) assert(flags == 48); return template end,
            IsA = function(_, cls) return cls == "/Game/Pal/Blueprint/UI/UserInterface/Map/WBP_Map_Body.WBP_Map_Body_C" end,
            GetWorld = function() return world end, IsVisible = function() return true end})
        s.bodies[#s.bodies+1] = b
        return b
    end
    function s.screen(by_region)
        return remote(object({MapBodyMap = {ForEach = function(_, visit)
            for region, body in pairs(by_region) do visit(remote(region), remote(body)) end
        end}, IsA = function(_, cls) return cls == "/Script/Pal.PalUIWorldMap" end,
            HasAnyFlags = function() return false end}))
    end
    load_mod("mods/client/PalMapReveal/Scripts/main.lua", {
        EObjectFlags = {RF_ClassDefaultObject = 16, RF_ArchetypeObject = 32},
        RegisterCustomEvent = function(name, cb) s[name] = cb end,
        Key = {F8 = 119}, ModifierKey = {CONTROL = 17},
        RegisterKeyBind = function(_, _, cb) s.key = cb end,
        ExecuteInGameThread = function(cb) cb() end,
        StaticFindObject = function(cls, tree, name, exact)
            assert(cls == nil and name == "Image_MapMask" and exact == false); return tree.mask or dead
        end,
        FindAllOf = function(class) assert(class == "WBP_Map_Body_C"); s.scans = s.scans + 1; return s.bodies end,
        print = function(msg) s.last = msg end,
    })
    return s
end

test("the region registry supplies both original map bodies including one not yet shown", function()
    local s = map_scene()
    local main, tree, template = s.body(false), s.body(false), s.body(true)
    tree.WidgetTree.mask, tree.Image_MapMask = tree.Image_MapMask, nil
    function tree:IsVisible() return false end
    local screen = s.screen({MainMap = main, Tree = tree})
    s.InitializeMapBody(screen); s.ChangeMap(screen)
    s.LoadAndApplyDefaultMaskTexture(remote(template))
    assert(s.writes == 2 and s.scans == 0 and tree.WidgetTree.mask.visibility == 2)
    assert(main.Cloud.visibility == 0 and tree.Icons.visibility == 0 and template.Image_MapMask.visibility == 0)
end)

test("mask initialization and reuse target the actual body without a timer or a window search", function()
    local s = map_scene()
    local map = s.body(false)
    s.InitializeMapBody(s.screen({}))
    s.LoadAndApplyDefaultMaskTexture(remote(map))
    assert(map.Image_MapMask.visibility == 2)
    map.Image_MapMask.visibility = 0
    s.ChangeMap(s.screen({MainMap = map}))
    assert(map.Image_MapMask.visibility == 2 and s.writes == 2 and s.scans == 0)
end)

test("manual map check counts the missing layer separately and skips template objects", function()
    local s = map_scene()
    s.body(true)
    local map = s.body(false)
    map.WidgetTree.mask, map.Image_MapMask = map.Image_MapMask, nil
    s.key(); assert(s.last:find("Live maps: 1") and s.last:find("layers: 1"))
    map.WidgetTree.mask = nil
    s.key(); assert(s.last:find("layers: 0") and s.scans == 2 and s.writes == 1)
end)

local slot_type = "/Script/Pal.PalGliderComponent"
local actor_type = "/Script/Pal.PalGliderObject"
local function name(text) return {ToString = function() return text end} end

local function glider_scene()
    local s = {events = {}, assets = {}, sets = 0, loads = 0, plays = 0, keys = {}, messages = {}}
    local function asset(path)
        local a = object({GetAddress = function() return path end,
            GetFullName = function() return "Object " .. path end})
        s.assets[path] = a
        return a
    end
    local empty = asset("/Invalid"); empty.valid = false
    s.fabric, s.pal, s.feather, s.dye = asset("/Fabric"), asset("/Pal"), asset("/Feather"), asset("/Dye")
    s.pal.Skeleton = asset("/Skeleton")
    s.animation = asset("/Flying"); s.animation.Skeleton = s.pal.Skeleton
    local source = object({GetSkeletalMeshAsset = function() return s.pal end,
        GetNumMaterials = function() return 1 end, GetMaterial = function() return s.feather end})
    local template = object({Mesh = source, GetMainMesh = function() return s.main_missing and empty or source end, StaticCharacterParameterComponent = object({
        GeneralBlendSpaceMap = {ForEach = function(_, f) f(remote(3), remote(s.animation)) end}})})
    s.class_name = "BP_Glider_Eagle_Tier2_C"
    s.target = object({mesh = s.fabric, OverrideMaterials = {s.dye},
        RelativeLocation = {X = 0, Y = 0, Z = 0}, RelativeScale3D = {X = 1, Y = 1, Z = 1},
        RelativeRotation = {Pitch = 0, Yaw = 0, Roll = 0}})
    function s.target:GetSkeletalMeshAsset() return self.mesh end
    function s.target:SetSkeletalMeshAsset(m) self.mesh = m; s.sets = s.sets + 1 end
    function s.target:GetMaterial(i) return self.OverrideMaterials[i+1] or empty end
    function s.target:SetMaterial(i, v) self.OverrideMaterials[i+1] = v end
    s.target.bNoSkeletonUpdate, s.target.bPauseAnims = true, true
    function s.target:IsComponentTickEnabled() return self.tick == true end
    function s.target:SetComponentTickEnabled(enabled) self.tick = enabled end
    function s.target:K2_SetWorldLocationAndRotation(loc, rot) self.world, self.world_rot = loc, rot end
    function s.target:PlayAnimation(anim, loop)
        assert(anim == s.animation and loop and self.tick and not self.bNoSkeletonUpdate and not self.bPauseAnims)
        s.plays = s.plays + 1
    end
    s.actor = asset("/Transient.Glider")
    function s.actor:IsA(t) return t == actor_type end
    function s.actor:GetMainMesh() return s.target end
    function s.actor:GetClass() return {GetFName = function() return name(s.class_name) end} end
    s.slot = object({CurrentGliderPalID = name("None"), CurrentGliderIndividualParameter = empty, IsA = function(_, t) return t == slot_type end,
        GetCurrentGliderObject = function() return s.actor end})
    local owner = object({GetComponentByClass = function(_, class)
        assert(class == s.assets[slot_type]); return s.slot
    end, K2_GetActorLocation = function() return {X = 100, Y = 200, Z = 50} end,
        K2_GetActorRotation = function() return {Pitch = 0, Yaw = 90, Roll = 0} end})
    s.assets[slot_type] = asset(slot_type)
    function s.actor:GetOwner() return owner end
    function s.slot:IsGliding() return false end
    function s.slot:GetCurrentGliderVisibility() return s.is_visible == true end
    function s.slot:HasGliderPal() return s.team_id ~= nil end
    function s.slot:TryGetGliderIndividualHandleFromOtomoHolder()
        return object({TryGetIndividualParameter = function()
            return object({GetCharacterID = function() return name(s.team_id) end})
        end})
    end
    local db = object({GetBPClass = function(_, id, noisy)
        assert(not noisy); s.looked_up = id:ToString(); return s.looked_up end})
    s.assets["/Script/Pal.Default__PalUtility"] = object({GetDatabaseCharacterParameter = function() return db end,
        GetDefaultObject = function() return template end, ClearOverrideMaterials = function(_, t) t.OverrideMaterials = {} end})
    s.assets["/Script/Engine.Default__KismetSystemLibrary"] = object({
        Conv_SoftClassReferenceToClass = function(_, ref) return (s.cold or ref == "Bad") and empty or template end,
        LoadClassAsset_Blocking = function(_, ref) s.loads = s.loads+1; return ref == "Bad" and empty or template end,
        -- 伞面与物种本体的世界包围盒不同：伞面中心在本体下方 200，宽度 100 对 80。
        GetComponentBounds = function(_, component)
            if component.mesh == s.pal then
                return {X = 0, Y = 0, Z = 300}, {X = 80, Y = 40, Z = 10}, 0
            end
            return {X = 0, Y = 0, Z = 100}, {X = 100, Y = 50, Z = 20}, 0
        end,
        PrintString = function(_, actor, text) s.screen = text end})
    s.assets["/Script/Engine.Default__KismetMathLibrary"] = object({
        ComposeRotators = function(_, a, b)
            return {Pitch = a.Pitch + b.Pitch, Yaw = a.Yaw + b.Yaw, Roll = a.Roll + b.Roll}
        end})    s.env = load_mod("mods/client/PalGliderVisual/Scripts/main.lua", {
        FName = name, StaticFindObject = function(path) return s.assets[path] or empty end,
        RegisterCustomEvent = function(event, cb) s.events[event] = cb end,
        RegisterLoadMapPreHook = function(cb) s.travel = cb end,
        print = function(message) s.messages[#s.messages + 1] = message end,
        FindAllOf = function() error("no global scanning") end})
    function s.visible(value) s.is_visible = value; s.events.OnChangeGliderVisibility(remote(s.slot), remote(value)) end
    function s.refresh(id)
        local h = s.env.hooks[actor_type..":RefreshSkin"]
        h.pre(remote(s.actor),remote(name(id))); h.post(remote(s.actor),remote(name(id)))
    end
    return s
end

test("a visible tier glider swaps in the species and places it on the player", function()
    for _, family in ipairs({"Eagle","FlyingManta","FlyingManta_Thunder","NegativeOctopus","NegativeOctopus_Neutral","WindChimes","WindChimes_Ice"}) do
        local s = glider_scene(); s.class_name = "BP_Glider_"..family.."_Tier4_C"
        s.visible(true)
        assert(s.target.mesh == s.pal and s.looked_up == family and s.plays == 1)
        -- 默认补偿来自实机调参结果：pitch -90 / yaw -90 / roll 0，位置 (20, 150, 0)。
        assert(s.target.RelativeRotation.Yaw == -90 and s.target.RelativeRotation.Roll == 0)
        assert(s.target.RelativeRotation.Pitch == -90)
        assert(math.abs(s.target.RelativeLocation.X - 20) < 0.5)
        assert(math.abs(s.target.RelativeLocation.Y - 150) < 0.5)
        assert(math.abs(s.target.RelativeLocation.Z) < 0.5)
        s.events.OnStartGliding(remote(s.actor))
        assert(s.sets == 1 and s.target:GetMaterial(0) == s.feather)
    end
end)

test("species base classes are recognised with the game's mixed naming", function()
    for _, case in ipairs({
        {"BP_Glider_EagleBase_C", "Eagle"},
        {"BP_Glider_FlyingMantaBase_C", "FlyingManta"},
        {"BP_Glider_FlyingManta_ThunderBase_C", "FlyingManta_Thunder"},
        {"BP_Glider_NegativeOctopus_NeutralBase_C", "NegativeOctopus_Neutral"},
        {"BP_Glider_WindChimes_Base_C", "WindChimes"},
        {"BP_Glider_WindChimes_Ice_Base_C", "WindChimes_Ice"},
    }) do
        local s = glider_scene(); s.class_name = case[1]
        s.visible(true)
        assert(s.target.mesh == s.pal and s.looked_up == case[2] and s.plays == 1, case[1])
    end
end)

test("the item glider base class stays a shared glider", function()
    local s = glider_scene(); s.class_name = "BP_Glider_Item_Base_C"
    s.visible(true)
    assert(s.sets == 0 and s.plays == 0) -- 普通伞基类不是搭档专属，不去查物种
    s.refresh("Eagle")
    assert(s.target.mesh == s.pal and s.plays == 0)
end)

test("a partner glider without a matching animation still restores the skeleton update", function()
    local s = glider_scene(); s.class_name = "BP_Glider_Eagle_Tier0_C"
    s.animation.Skeleton = s.fabric
    s.visible(true)
    assert(s.target.mesh == s.pal and s.plays == 0)
    assert(not s.target.bNoSkeletonUpdate and not s.target.bPauseAnims and s.target.tick)
end)

test("the partner gear start event can precede publication of the current gear in the player slot", function()
    local s = glider_scene()
    s.slot.GetCurrentGliderObject = function() return s.fabric end
    s.events.OnStartGliding(remote(s.actor))
    assert(s.looked_up == "Eagle" and s.sets == 1 and s.plays == 1)
    s.events.OnEndGliding(remote(s.actor))
    assert(not s.target.tick and s.target.bPauseAnims and s.target.bNoSkeletonUpdate)
    assert(s.target.mesh == s.fabric and s.target.RelativeLocation.Z == 0 and s.target.RelativeScale3D.X == 1)
    assert(s.target.RelativeRotation.Yaw == 0)
    s.events.OnStartGliding(remote(s.actor))
    assert(s.sets == 3 and s.plays == 2 and s.target.tick) -- 换模 + 收伞还原 + 再次换模
    local first_rank = glider_scene()
    first_rank.class_name = "BP_Glider_WindChimes_Base_C"
    first_rank.events.OnStartGliding(remote(first_rank.actor))
    assert(first_rank.looked_up == "WindChimes" and first_rank.plays == 1)
end)

test("the game's skin request dresses a shared glider and restores the original dyed gear", function()
    local s = glider_scene(); s.class_name = "BP_Glider_Good_C"
    s.visible(true); assert(s.sets == 0)
    s.refresh("FlyingManta"); assert(s.target.mesh == s.pal and s.target:GetMaterial(0) == s.feather)
    s.refresh("None"); assert(s.target.mesh == s.fabric and s.target:GetMaterial(0) == s.dye and s.plays == 0)
    s.slot.CurrentGliderPalID = name("Eagle"); s.events.OnStartGliding(remote(s.slot))
    s.visible(false); assert(s.target.mesh == s.fabric and s.target:GetMaterial(0) == s.dye)
end)

test("shared equipment can use the selected party partner before the species ID is replicated", function()
    local s = glider_scene(); s.class_name = "BP_Glider_Old_C"; s.team_id = "Eagle"
    s.env.hooks[slot_type..":OnRep_CurrentGliderSoftClass"].post(remote(s.slot))
    assert(s.looked_up == nil)
    s.visible(true); assert(s.looked_up == "Eagle" and s.target.mesh == s.pal)
    s.team_id = nil
    s.events.OnEndGliding(remote(s.slot)); assert(s.target.mesh == s.fabric)
end)

test("a skin refresh without an ID keeps the partner selected on the visible shared glider", function()
    local s = glider_scene()
    s.class_name = "BP_Glider_Good_C"
    s.team_id = "Eagle"
    s.visible(true)
    for _ = 1, 100 do s.refresh("None") end
    assert(s.sets == 1 and s.target.mesh == s.pal and s.target:GetMaterial(0) == s.feather)
    s.team_id = nil
    s.refresh("None")
    assert(s.target.mesh == s.fabric and s.target:GetMaterial(0) == s.dye)
end)

test("the selected individual identifies a shared glider before its replicated ID arrives", function()
    local s = glider_scene()
    s.class_name = "BP_Glider_Good_C"
    s.slot.CurrentGliderIndividualParameter = object({GetCharacterID = function() return name("FlyingManta") end})
    s.visible(true)
    assert(s.looked_up == "FlyingManta" and s.target.mesh == s.pal)
end)

test("a species default with only the inherited mesh still supplies its visual", function()
    local s = glider_scene()
    s.main_missing = true
    s.visible(true)
    assert(s.target.mesh == s.pal and s.plays == 1)
end)

test("late actor, late variant ID and a refresh on an existing mesh", function()
    local s = glider_scene(); s.class_name = "BP_Glider_FlyingManta_Tier0_C"; s.actor.valid = false
    s.visible(true); assert(s.sets == 0)
    s.actor.valid = true
    s.env.hooks[slot_type..":OnRep_CurrentGliderSoftClass"].post(remote(s.slot))
    assert(s.looked_up == "FlyingManta")
    s.slot.CurrentGliderPalID = name("FlyingManta_Thunder")
    s.env.hooks[slot_type..":OnRep_CurrentGliderPalID"].post(remote(s.slot))
    assert(s.looked_up == "FlyingManta_Thunder")
    s.target.OverrideMaterials = {s.dye}; s.refresh("FlyingManta_Thunder")
    assert(s.sets == 1 and s.target:GetMaterial(0) == s.feather and s.looked_up == "FlyingManta_Thunder")
end)

test("initial skin refresh defers a cold load until the glider is shown", function()
    local s = glider_scene(); s.cold = true
    for _ = 1, 20 do s.refresh("Eagle") end
    assert(s.loads == 0 and s.sets == 0, "Hidden glider synchronously loaded a species")
    s.visible(true)
    assert(s.loads == 1 and s.sets == 1 and s.looked_up == "Eagle")
    s.slot.GetCurrentGliderObject = function() return s.fabric end
    s.refresh("Eagle")
    assert(s.loads == 1) -- A different actor belonging to the same visible slot stays cold.
end)

test("unshown equipment skips even resident species, meshes and materials", function()
    local s = glider_scene()
    for i = 1, 1000 do s.refresh("Eagle") end
    assert(s.looked_up == nil and s.loads == 0 and s.sets == 0)
    s.visible(true)
    assert(s.looked_up == "Eagle" and s.target.mesh == s.pal)
end)

test("a late glider owner defers all work until the partner gear starts", function()
    local s = glider_scene()
    function s.actor:GetOwner() return object({valid = false}) end
    s.cold = true; s.refresh("Eagle")
    assert(s.loads == 0 and s.sets == 0)
    s.cold = false; s.refresh("Eagle")
    assert(s.sets == 0 and s.looked_up == nil)
    s.events.OnStartGliding(remote(s.actor))
    assert(s.sets == 1 and s.loads == 0 and s.looked_up == "Eagle")
end)

test("jetpacks, unselected gear, missing species and incompatible animations", function()
    local s = glider_scene(); s.actor.bIsJetpackType = true; s.refresh("Eagle"); s.visible(true)
    assert(s.sets == 0 and s.looked_up == nil)
    s.actor.bIsJetpackType = false; s.class_name = "BP_Glider_Good_C"; s.refresh("None"); s.refresh("Bad")
    assert(s.loads == 1 and s.sets == 0 and s.target:GetMaterial(0) == s.dye)
    s.class_name = "BP_Glider_Eagle_Tier0_C"; s.cold = true; s.animation.Skeleton = s.fabric; s.visible(true)
    assert(s.loads == 2 and s.sets == 1 and s.plays == 0)
end)
print(string.format("%d runtime logic tests passed; native game validation still required.", count))
