local helpers = require("UEHelpers")
local utility_path = "/Script/Pal.Default__PalUtility"

-- The server's base registry already contains each loaded model. Buildings,
-- trees and dropped items do not need to enter Lua when a save is restored.
LoopInGameThreadWithDelay(15000, function()
    local instance = helpers.GetGameInstance()
    if not instance:IsValid() then return false end
    local world = instance:GetWorld()
    if not world:IsValid() then return false end
    local utility = StaticFindObject(utility_path)
    local state = utility:GetPalGameStateInGame(world)
    if not state:IsValid() then return false end
    local manager = utility:GetBaseCampManager(world)
    if not manager:IsValid() then return false end

    local ranges = manager.BaseCampSignificanceInfoList
    for i = 1, #ranges do
        local row = ranges[i]
        if not row.bMergeDropItems then row.bMergeDropItems = true end
    end

    local registry = state.BaseCampReplicator
    if registry:IsValid() then
        local entries = registry.RepInfoArray.Items
        for i = 1, #entries do
            local base = entries[i].BaseCamp
            if base:IsValid() then
                local settings = base.SignificanceInfo
                if not settings.bMergeDropItems then settings.bMergeDropItems = true end
            end
        end
    end
    return false
end)
