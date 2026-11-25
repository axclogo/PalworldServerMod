local slot_class = "/Script/Pal.PalGliderComponent"
local actor_class = "/Script/Pal.PalGliderObject"
local utility_path = "/Script/Pal.Default__PalUtility"
local system_path = "/Script/Engine.Default__KismetSystemLibrary"

-- 换模后的补偿，全部基于组件自身的相对属性（实测可用；世界坐标接口在本构建不可调用）。
-- pitch/yaw/roll：组件相对旋转（度，绝对写入，不继承伞面的 -90 翻滚）
-- forward/right：沿本体朝向的前后左右（厘米）；x/y/z：额外父空间偏移（厘米）
-- scale：缩放倍数。键对应 partner_family()，未列出的物种用 default。
local ADJUST = {
    -- 2026-11-26 实机调出的天擒鸟姿态（F8 记录所得）
    default = {pitch = -90, yaw = -90, roll = 0, forward = 0, right = 0, x = 20, y = 150, z = 0, scale = 1},
    Eagle = {pitch = -90, yaw = -90, roll = 0, forward = 0, right = 0, x = 20, y = 150, z = 0, scale = 1},
}

local original = {}

local function path_of(obj)
    if obj:IsValid() then return obj:GetFullName():match("^%S+ (.+)$") end
end

local function snapshot(target, current_path)
    local loc, scale, rot = target.RelativeLocation, target.RelativeScale3D, target.RelativeRotation
    local materials = {}
    for index = 1, #target.OverrideMaterials do
        materials[index - 1] = path_of(target.OverrideMaterials[index])
    end
    return {
        mesh = current_path, shown = nil, materials = materials,
        loc = {X = loc.X, Y = loc.Y, Z = loc.Z},
        scale = {X = scale.X, Y = scale.Y, Z = scale.Z},
        rot = {Pitch = rot.Pitch, Yaw = rot.Yaw, Roll = rot.Roll},
        tick = target:IsComponentTickEnabled(),
        frozen = target.bNoSkeletonUpdate,
        paused = target.bPauseAnims,
    }
end

local function apply_adjust(target, record, adjust)
    local rot = target.RelativeRotation
    rot.Pitch, rot.Yaw, rot.Roll = adjust.pitch or 0, adjust.yaw or 0, adjust.roll or 0
    target.RelativeRotation = rot
    if record and record.loc then
        local yaw_rad = math.rad(rot.Yaw or 0)
        local forward, side = adjust.forward or 0, adjust.right or 0
        local loc = target.RelativeLocation
        loc.X = record.loc.X + math.cos(yaw_rad) * forward - math.sin(yaw_rad) * side + (adjust.x or 0)
        loc.Y = record.loc.Y + math.sin(yaw_rad) * forward + math.cos(yaw_rad) * side + (adjust.y or 0)
        loc.Z = record.loc.Z + (adjust.z or 0)
        target.RelativeLocation = loc
    end
    local scale = target.RelativeScale3D
    if record and record.scale then
        local ratio = adjust.scale or 1
        scale.X, scale.Y, scale.Z = record.scale.X * ratio, record.scale.Y * ratio, record.scale.Z * ratio
    end
    target.RelativeScale3D = scale
end

local function restore(actor)
    if not actor:IsValid() then return end
    local key = path_of(actor)
    local saved = original[key]
    if not saved then return end
    original[key] = nil
    local target = actor:GetMainMesh()
    if not target:IsValid() then return end
    if path_of(target:GetSkeletalMeshAsset()) == saved.shown then
        local mesh = StaticFindObject(saved.mesh)
        if mesh:IsValid() then
            target:SetSkeletalMeshAsset(mesh)
            StaticFindObject(utility_path):ClearOverrideMaterials(target)
            for index, path in pairs(saved.materials) do
                local material = StaticFindObject(path)
                if material:IsValid() then target:SetMaterial(index, material) end
            end
        end
    end
    local loc = target.RelativeLocation
    loc.X, loc.Y, loc.Z = saved.loc.X, saved.loc.Y, saved.loc.Z
    target.RelativeLocation = loc
    local rot = target.RelativeRotation
    rot.Pitch, rot.Yaw, rot.Roll = saved.rot.Pitch, saved.rot.Yaw, saved.rot.Roll
    target.RelativeRotation = rot
    local scale = target.RelativeScale3D
    scale.X, scale.Y, scale.Z = saved.scale.X, saved.scale.Y, saved.scale.Z
    target.RelativeScale3D = scale
    target.bNoSkeletonUpdate = saved.frozen
    target.bPauseAnims = saved.paused
    target:SetComponentTickEnabled(saved.tick)
end

local function flying_animation(pal, mesh)
    local params = pal.StaticCharacterParameterComponent
    if not params:IsValid() then return end
    local fallback, flying
    params.GeneralBlendSpaceMap:ForEach(function(key, value)
        local kind = key:get()
        if kind ~= 1 and kind ~= 3 then return end
        local blend = value:get()
        if not blend:IsValid() or blend.Skeleton:GetAddress() ~= mesh.Skeleton:GetAddress() then return end
        if kind == 3 then flying = blend; return true end
        fallback = blend
    end)
    return flying or fallback
end

local function visible_slot_for(actor)
    local owner = actor:GetOwner()
    if not owner:IsValid() then return nil end
    local slot = owner:GetComponentByClass(StaticFindObject(slot_class))
    if not slot:IsValid() then return nil end
    if not (slot:IsGliding() or slot:GetCurrentGliderVisibility()) then return nil end
    local current = slot:GetCurrentGliderObject()
    if current:IsValid() and current:GetAddress() == actor:GetAddress() then return slot end
end

local function selected_partner(slot)
    local id = slot.CurrentGliderPalID
    if id:ToString() ~= "None" then return id end
    local active = slot.CurrentGliderIndividualParameter
    if active:IsValid() then id = active:GetCharacterID() end
    if id:ToString() == "None" and slot:HasGliderPal() then
        local handle = slot:TryGetGliderIndividualHandleFromOtomoHolder()
        if handle:IsValid() then
            local param = handle:TryGetIndividualParameter()
            if param:IsValid() then id = param:GetCharacterID() end
        end
    end
    return id
end

local function partner_family(actor)
    local name = actor:GetClass():GetFName():ToString()
    local base = name:match("^BP_Glider_(.+)Base_C$")
    if base then
        base = base:gsub("_$", "")
        if base ~= "Item" then return base end
        return nil
    end
    return name:match("^BP_Glider_(.+)_Tier%d+_C$")
end

local function show(actor, id)
    local family = partner_family(actor)
    local selected = id:ToString()
    if family then
        if selected ~= family and selected:sub(1, #family + 1) ~= family .. "_" then id = FName(family) end
    elseif selected == "None" then
        restore(actor)
        return
    end
    local target = actor:GetMainMesh()
    if not target:IsValid() then
        print("[PalGliderVisual] " .. selected .. ": glider main mesh missing\n")
        return
    end
    local utility = StaticFindObject(utility_path)
    local system = StaticFindObject(system_path)
    local db = utility:GetDatabaseCharacterParameter(actor)
    if not db:IsValid() then
        print("[PalGliderVisual] " .. selected .. ": database missing\n")
        return
    end
    local ref = db:GetBPClass(id, false)
    local class = system:Conv_SoftClassReferenceToClass(ref)
    if not class:IsValid() then
        class = system:LoadClassAsset_Blocking(ref)
    end
    if not class:IsValid() then
        print("[PalGliderVisual] " .. selected .. ": class not loadable\n")
        return
    end
    local pal = utility:GetDefaultObject(class)
    if not pal:IsValid() then
        print("[PalGliderVisual] " .. selected .. ": default object invalid\n")
        return
    end
    local source = pal:GetMainMesh()
    if not source:IsValid() then source = pal.Mesh end
    if not source:IsValid() then
        print("[PalGliderVisual] " .. selected .. ": pal mesh missing\n")
        return
    end
    local mesh = source:GetSkeletalMeshAsset()
    if not mesh:IsValid() then
        print("[PalGliderVisual] " .. selected .. ": skeletal mesh missing\n")
        return
    end
    local current = target:GetSkeletalMeshAsset()
    local current_path = path_of(current)
    local changed = current:GetAddress() ~= mesh:GetAddress()
    local key = path_of(actor)
    local record = original[key]
    if record and record.shown ~= path_of(mesh) then
        record, original[key] = nil, nil
    end
    if changed then
        if not record then
            if not current_path then return end
            record = snapshot(target, current_path)
            original[key] = record
        end
        record.shown = path_of(mesh)
        target:SetSkeletalMeshAsset(mesh)
        utility:ClearOverrideMaterials(target)
    end
    for index = 0, source:GetNumMaterials() - 1 do
        local material = source:GetMaterial(index)
        if material:IsValid() and target:GetMaterial(index):GetAddress() ~= material:GetAddress() then
            target:SetMaterial(index, material)
        end
    end
    if family then
        if record and not changed then return end
        if not record then
            record = snapshot(target, current_path or path_of(mesh))
            record.shown = path_of(mesh)
            original[key] = record
        end
        apply_adjust(target, record, ADJUST[family] or ADJUST.default)
        target.bNoSkeletonUpdate = false
        target.bPauseAnims = false
        target:SetComponentTickEnabled(true)
        local animation = flying_animation(pal, mesh)
        if animation then
            target:PlayAnimation(animation, true)
        else
            print("[PalGliderVisual] " .. id:ToString() .. " no flying blend space\n")
        end
    end
end

local function show_slot(slot)
    local actor = slot:GetCurrentGliderObject()
    if not actor:IsValid() or actor.bIsJetpackType then return end
    show(actor, selected_partner(slot))
end

local function replicated(context)
    local slot = context:get()
    if slot:IsGliding() or slot:GetCurrentGliderVisibility() then show_slot(slot) end
end

RegisterCustomEvent("OnStartGliding", function(context)
    local source = context:get()
    if source:IsA(slot_class) then
        show_slot(source)
    elseif source:IsA(actor_class) and not source.bIsJetpackType then
        local family = partner_family(source)
        local slot = visible_slot_for(source)
        if slot then show(source, selected_partner(slot))
        elseif family then show(source, FName(family)) end
    end
end)
RegisterCustomEvent("OnChangeGliderVisibility", function(context, visible)
    local slot = context:get()
    if not slot:IsA(slot_class) then return end
    if visible:get() then show_slot(slot) else restore(slot:GetCurrentGliderObject()) end
end)
RegisterCustomEvent("OnEndGliding", function(context)
    local source = context:get()
    if source:IsA(actor_class) then restore(source)
    elseif source:IsA(slot_class) then restore(source:GetCurrentGliderObject()) end
end)
RegisterHook(slot_class .. ":OnRep_CurrentGliderPalID", function() end, replicated)
RegisterHook(slot_class .. ":OnRep_CurrentGliderSoftClass", function() end, replicated)
RegisterHook(actor_class .. ":RefreshSkin", function() end, function(context, pal_id)
    local actor = context:get()
    if not actor:IsValid() or actor.bIsJetpackType then return end
    local slot = visible_slot_for(actor)
    if not slot then return end
    local id = pal_id:get()
    if id:ToString() == "None" then id = selected_partner(slot) end
    local ok, err = pcall(show, actor, id)
    if not ok then print("[PalGliderVisual] error: " .. tostring(err) .. "\n") end
end)
RegisterLoadMapPreHook(function() original = {} end)
