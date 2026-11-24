local slot_class = "/Script/Pal.PalGliderComponent"
local actor_class = "/Script/Pal.PalGliderObject"
local utility_path = "/Script/Pal.Default__PalUtility"
local system_path = "/Script/Engine.Default__KismetSystemLibrary"

-- A shared equipment actor may switch back to a fabric glider. Keep paths only:
-- queued or retained UE4SS wrappers could outlive their UObjects after travel.
local original = {}
local function path_of(obj)
    if obj:IsValid() then return obj:GetFullName():match("^%S+ (.+)$") end
end

local function restore(actor)
    if not actor:IsValid() then return end
    local key = path_of(actor)
    local saved = original[key]
    if not saved then return end
    original[key] = nil
    local target = actor:GetMainMesh()
    if not target:IsValid() then return end
    if saved.tick ~= nil then
        target.bNoSkeletonUpdate = saved.frozen
        target.bPauseAnims = saved.paused
        target:SetComponentTickEnabled(saved.tick)
        return
    end
    if path_of(target:GetSkeletalMeshAsset()) ~= saved.shown then return end
    local mesh = StaticFindObject(saved.mesh)
    if not mesh:IsValid() then return end
    target:SetSkeletalMeshAsset(mesh)
    StaticFindObject(utility_path):ClearOverrideMaterials(target)
    for index, path in pairs(saved.materials) do
        local material = StaticFindObject(path)
        if material:IsValid() then target:SetMaterial(index, material) end
    end
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
    -- The game's partner list assigns the base class itself at WindChimes rank one.
    if name == "BP_Glider_WindChimes_Base_C" then return "WindChimes" end
    return name:match("^BP_Glider_(.+)_Tier%d+_C$")
end

local function show(actor, id)
    local family = partner_family(actor)
    local selected = id:ToString()
    if family then
        -- Each tier is a dedicated partner actor. It can arrive before the replicated ID.
        if selected ~= family and selected:sub(1, #family + 1) ~= family .. "_" then id = FName(family) end
    elseif selected == "None" then
        restore(actor)
        return
    end
    local target = actor:GetMainMesh()
    if not target:IsValid() then return end
    local utility = StaticFindObject(utility_path)
    local system = StaticFindObject(system_path)
    local db = utility:GetDatabaseCharacterParameter(actor)
    if not db:IsValid() then return end
    local ref = db:GetBPClass(id, false)
    local class = system:Conv_SoftClassReferenceToClass(ref)
    if not class:IsValid() then
        class = system:LoadClassAsset_Blocking(ref)
    end
    if not class:IsValid() then return end
    local pal = utility:GetDefaultObject(class)
    if not pal:IsValid() then return end
    local source = pal:GetMainMesh()
    if not source:IsValid() then source = pal.Mesh end
    if not source:IsValid() then return end
    local mesh = source:GetSkeletalMeshAsset()
    if not mesh:IsValid() then return end
    local current = target:GetSkeletalMeshAsset()
    local changed = current:GetAddress() ~= mesh:GetAddress()
    if changed then
        if not family then
            local key, current_path = path_of(actor), path_of(current)
            if not current_path then return end
            local saved = original[key]
            if not saved or current_path ~= saved.shown then
                saved = {mesh = current_path, materials = {}}
                for i = 1, #target.OverrideMaterials do
                    saved.materials[i - 1] = path_of(target.OverrideMaterials[i])
                end
                original[key] = saved
            end
            saved.shown = path_of(mesh)
        end
        target:SetSkeletalMeshAsset(mesh)
        utility:ClearOverrideMaterials(target)
    end
    for i = 0, source:GetNumMaterials() - 1 do
        local material = source:GetMaterial(i)
        if material:IsValid() and target:GetMaterial(i):GetAddress() ~= material:GetAddress() then
            target:SetMaterial(i, material)
        end
    end
    if family then
        local key = path_of(actor)
        if original[key] and not changed then return end
        local animation = flying_animation(pal, mesh)
        if animation then
            -- Some partner gear freezes the skeleton and disables ticking while stowed.
            original[key] = original[key] or {tick = target:IsComponentTickEnabled(),
                frozen = target.bNoSkeletonUpdate, paused = target.bPauseAnims}
            target.bNoSkeletonUpdate = false
            target.bPauseAnims = false
            target:SetComponentTickEnabled(true)
            target:PlayAnimation(animation, true)
        end
    end
end

local function show_slot(slot)
    local actor = slot:GetCurrentGliderObject()
    if not actor:IsValid() or actor.bIsJetpackType then return end
    local id = selected_partner(slot)
    show(actor, id)
end

local function replicated(context)
    local slot = context:get()
    if slot:IsGliding() or slot:GetCurrentGliderVisibility() then show_slot(slot) end
end

-- UE4SS dispatches these Blueprint callbacks after the visual event body.
RegisterCustomEvent("OnStartGliding", function(context)
    local source = context:get()
    if source:IsA(slot_class) then
        show_slot(source)
    elseif source:IsA(actor_class) and not source.bIsJetpackType then
        -- The partner gear itself receives the delegate, even before the slot
        -- exposes its current actor on a remote client.
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
    show(actor, id)
end)
RegisterLoadMapPreHook(function() original = {} end)
