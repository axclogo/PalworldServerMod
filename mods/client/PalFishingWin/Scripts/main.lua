local rod_states = StaticFindObject("/Script/Pal.EPalFishingRodState")
local wait_hit
if rod_states:IsValid() then
    rod_states:ForEachName(function(name, value)
        if name:ToString():match("[^:]+$") == "WaitHit" then
            wait_hit = value
            return true
        end
    end)
end
if wait_hit == nil then
    print("[PalFishingWin] WaitHit missing in EPalFishingRodState. Use the normal fishing button.\n")
    return
end

RegisterHook("/Script/Pal.PalFishingComponent:OnChangeRodState", function(context, state_arg)
    if state_arg:get() ~= wait_hit then return end
    local rod = context:get()
    if not rod:IsValid() then return end
    local character = rod:GetOwner()
    if not character:IsValid() or not character:IsA("/Script/Pal.PalPlayerCharacter") then return end
    local controller = character:GetPalPlayerController()
    if controller:IsValid() and controller:IsLocalPlayerController() and not rod:IsFishingButtonPressed() then
        rod:OnPressedFishingButton()
    end
end)

print("[PalFishingWin] Fishing state hook registered.\n")
