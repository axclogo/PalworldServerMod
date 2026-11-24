local body_class = "/Game/Pal/Blueprint/UI/UserInterface/Map/WBP_Map_Body.WBP_Map_Body_C"
local template_flags = EObjectFlags.RF_ClassDefaultObject | EObjectFlags.RF_ArchetypeObject
local hidden = 2 -- ESlateVisibility::Hidden

local function hide_mask(body)
    if not body or not body:IsValid() or not body:IsA(body_class)
        or body:HasAnyFlags(template_flags) or not body:GetWorld():IsValid() then return false end
    local mask = body.Image_MapMask
    if not mask or not mask:IsValid() then
        local tree = body.WidgetTree
        if tree and tree:IsValid() then mask = StaticFindObject(nil, tree, "Image_MapMask", false) end
    end
    if not mask or not mask:IsValid() or not mask:IsA("/Script/UMG.Image") then return false end
    if mask:GetVisibility() ~= hidden then mask:SetVisibility(hidden) end
    return mask:GetVisibility() == hidden
end

-- Setup applies the mask material on the map body. The screen also registers
-- its concrete map bodies by region in InitializeMapBody and reuses them in ChangeMap.
RegisterCustomEvent("LoadAndApplyDefaultMaskTexture", function(context)
    hide_mask(context:get())
end)
local function hide_screen_masks(context)
    local screen = context:get()
    if not screen:IsA("/Script/Pal.PalUIWorldMap") or screen:HasAnyFlags(template_flags) then return end
    local bodies = screen.MapBodyMap
    if bodies then bodies:ForEach(function(_, value) hide_mask(value:get()) end) end
end
RegisterCustomEvent("InitializeMapBody", hide_screen_masks)
RegisterCustomEvent("ChangeMap", hide_screen_masks)

RegisterKeyBind(Key.F8, {ModifierKey.CONTROL}, function()
    ExecuteInGameThread(function()
        local live, ready = 0, 0
        for _, body in ipairs(FindAllOf("WBP_Map_Body_C") or {}) do
            if not body:HasAnyFlags(template_flags) and body:GetWorld():IsValid() and body:IsVisible() then
                live = live + 1
                if hide_mask(body) then ready = ready + 1 end
            end
        end
        print(string.format("[PalMapReveal] Live maps: %d, hidden Image_MapMask layers: %d.\n", live, ready))
    end)
end)
