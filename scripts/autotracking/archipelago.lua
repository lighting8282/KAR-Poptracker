
require("scripts/autotracking/item_mapping")
require("scripts/autotracking/location_mapping")

CUR_INDEX = -1
--SLOT_DATA = nil

ALL_LOCATIONS = {}
SLOT_DATA = {}

MANUAL_CHECKED = true
ROOM_SEED = "default"
TROLL_PLAYER = false

-- Top Ride control machines. These are lit purely from a live room connection (both when machines
-- aren't gated, the other from a received starter when they are), never from restored save state.
TR_CONTROL_MACHINES = { "machine_free_star", "machine_steer_star" }

-- "Fill in 100 boxes" counters: map each AP location id to its mode so the autotracker can count
-- checked boxes per mode. Stadium checks count toward City Trial (mirrors the apworld). The three
-- Fill-in-100 cells (ids 56/145/360) are excluded so they never count toward their own threshold.
local function _fill_startswith(s, prefix) return type(s) == "string" and s:sub(1, #prefix) == prefix end
FILL_MODE_OF = {}
do
    local exclude = { [56] = true, [145] = true, [360] = true }
    for id, paths in pairs(LOCATION_MAPPING) do
        if not exclude[id] and paths and paths[1] then
            local p = paths[1]
            if _fill_startswith(p, "@City Trial") or _fill_startswith(p, "@Stadium") then
                FILL_MODE_OF[id] = "ct"
            elseif _fill_startswith(p, "@Air Ride") then
                FILL_MODE_OF[id] = "ar"
            elseif _fill_startswith(p, "@Top Ride") then
                FILL_MODE_OF[id] = "tr"
            end
        end
    end
end

-- Recount checked boxes per mode into the fill_count_* consumables, which drive the "$FILL_AT_LEAST"
-- gate on the "Fill in over 100 Checklist blocks!" cells. Counts completed checks only (not filler
-- items). Called from onClear (initial/replay) and onLocation (live).
function UpdateFillCounters()
    if not Archipelago or not Archipelago.CheckedLocations then return end
    local cnt = { ct = 0, ar = 0, tr = 0 }
    for _, id in pairs(Archipelago.CheckedLocations) do
        local m = FILL_MODE_OF[id]
        if m then cnt[m] = cnt[m] + 1 end
    end
    for m, code in pairs({ ct = "fill_count_ct", ar = "fill_count_ar", tr = "fill_count_tr" }) do
        local obj = Tracker:FindObjectForCode(code)
        if obj then obj.AcquiredCount = cnt[m] end
    end
end

if Highlight then
    HIGHLIGHT_LEVEL= {
        [0] = Highlight.Unspecified,
        [10] = Highlight.NoPriority,
        [20] = Highlight.Avoid,
        [30] = Highlight.Priority,
        [40] = Highlight.None,
        [100] = Highlight.Unspecified, --Filler
        [101] = Highlight.Priority, --Progression
        [102] = Highlight.NoPriority, --Useful
        [103] = Highlight.Priority, -- Prog + Useful
        [104] = Highlight.Avoid, --Trap
        [105] = Highlight.Priority, -- Prog + Trap
        [106] = Highlight.NoPriority, -- Useful + Trap
        [107] = Highlight.Priority, -- Prog + Useful + Trap
    }
end

Troll_Lookup = {
    ["solarcell"] = true,
    ["earthor"] = true,
}

function dump_table(o, depth)
    if depth == nil then
        depth = 0
    end
    if type(o) == 'table' then
        local tabs = ('\t'):rep(depth)
        local tabs2 = ('\t'):rep(depth + 1)
        local s = '{\n'
        for k, v in pairs(o) do
            if type(k) ~= 'number' then
                k = '"' .. k .. '"'
            end
            s = s .. tabs2 .. '[' .. k .. '] = ' .. dump_table(v, depth + 1) .. ',\n'
        end
        return s .. tabs .. '}'
    else
        return tostring(o)
    end
end

function LocationHandler(location)
    if MANUAL_CHECKED then
        local custom_storage_item = Tracker:FindObjectForCode("manual_location_storage").ItemState
        if not custom_storage_item then
            return
        end
        if Archipelago.PlayerNumber == -1 then -- not connected
            if ROOM_SEED ~= "default" then -- seed is from previous connection
                ROOM_SEED = "default"
                custom_storage_item.MANUAL_LOCATIONS["default"] = {}
            else -- seed is default
            end
        end
        local full_path = location.FullID
        if not custom_storage_item.MANUAL_LOCATIONS[ROOM_SEED] then
            custom_storage_item.MANUAL_LOCATIONS[ROOM_SEED] = {}
        end
        if location.AvailableChestCount < location.ChestCount then --add to list
            -- print("add to list")
            custom_storage_item.MANUAL_LOCATIONS[ROOM_SEED][full_path] = location.AvailableChestCount
        else --remove from list of set back to max chestcount
            -- print("remove from list")
            custom_storage_item.MANUAL_LOCATIONS[ROOM_SEED][full_path] = nil
        end
    end
    -- local custom_storage_item = Tracker:FindObjectForCode("manual_location_storage").ItemState
    -- print(dump_table(storage_item.ItemState.MANUAL_LOCATIONS))
    ForceUpdate() -- 
end

function ForceUpdate()
    local update = Tracker:FindObjectForCode("update")
    if update == nil then
        return
    end
    update.Active = not update.Active
end

function onClearHandler(slot_data)
    local clear_timer = os.clock()
    
    ScriptHost:RemoveWatchForCode("StateChange")
    -- Disable tracker updates.
    Tracker.BulkUpdate = true
    -- Use a protected call so that tracker updates always get enabled again, even if an error occurred.
    local ok, err = pcall(onClear, slot_data)
    -- Apply slot-data-driven indicators (links, progression, seed settings) independently of onClear's
    -- reset pass, so they still light up even if the reset pass errors out partway through.
    local sok, serr = pcall(applyProgressionSettings, slot_data)
    if not sok then
        print("Error: applyProgressionSettings failed:")
        print(serr)
    end
    -- Enable tracker updates again.
    if ok then
        -- Defer re-enabling tracker updates until the next frame, which doesn't happen until all received items/cleared
        -- locations from AP have been processed.
        local handlerName = "AP onClearHandler"
        local function frameCallback()
            ScriptHost:AddWatchForCode("StateChange", "*", StateChanged)
            ScriptHost:RemoveOnFrameHandler(handlerName)
            Tracker.BulkUpdate = false
            ForceUpdate()
            print(string.format("Time taken total: %.2f", os.clock() - clear_timer))
        end
        ScriptHost:AddOnFrameHandler(handlerName, frameCallback)
    else
        Tracker.BulkUpdate = false
        print("Error: onClear failed:")
        print(err)
    end
end

function preOnClear()
    PLAYER_ID = Archipelago.PlayerNumber or -1
	TEAM_NUMBER = Archipelago.TeamNumber or 0
    if Archipelago.PlayerNumber > -1 then
        for key, _ in pairs(Troll_Lookup) do
            if string.find(string.lower(Archipelago:GetPlayerAlias(PLAYER_ID)), key, 1, true) ~= nil then
                TROLL_PLAYER = true
                break
            end
        end
        if #ALL_LOCATIONS > 0 then
            ALL_LOCATIONS = {}
        end
        for _, value in pairs(Archipelago.MissingLocations) do
            table.insert(ALL_LOCATIONS, #ALL_LOCATIONS + 1, value)
        end

        for _, value in pairs(Archipelago.CheckedLocations) do
            table.insert(ALL_LOCATIONS, #ALL_LOCATIONS + 1, value)
        end
        HINTS_ID = "_read_hints_"..TEAM_NUMBER.."_"..PLAYER_ID
        Archipelago:SetNotify({HINTS_ID})
        Archipelago:Get({HINTS_ID})
    end


    -- print(Archipelago.Seed)
    local seed_base = (Archipelago.Seed or tostring(#ALL_LOCATIONS)).."_"..Archipelago.TeamNumber.."_"..Archipelago.PlayerNumber
    if ROOM_SEED == "default" or ROOM_SEED ~= seed_base then -- seed is default or from previous connection

        ROOM_SEED = seed_base --something like 2345_0_12
        for _, custom_item_code in pairs({"manual_location_storage"}) do -- add more to the table if you created more storage cache items
            local custom_storage_item = Tracker:FindObjectForCode(custom_item_code).ItemState
            if custom_storage_item then
                if #custom_storage_item.MANUAL_LOCATIONS > 10 then
                    custom_storage_item.MANUAL_LOCATIONS[custom_storage_item.MANUAL_LOCATIONS_ORDER[1]] = nil
                    table.remove(custom_storage_item.MANUAL_LOCATIONS_ORDER, 1)
                end
                if custom_storage_item.MANUAL_LOCATIONS[ROOM_SEED] == nil then
                    custom_storage_item.MANUAL_LOCATIONS[ROOM_SEED] = {}
                    table.insert(custom_storage_item.MANUAL_LOCATIONS_ORDER, ROOM_SEED)
                end
            end
        end
    else -- seed is from previous connection
        -- do nothing
    end
end

function onClear(slot_data)
    MANUAL_CHECKED = false
    local custom_storage_item = Tracker:FindObjectForCode("manual_location_storage").ItemState
    if custom_storage_item == nil then
        CreateLuaManualStorageItem("manual_location_storage")
        custom_storage_item = Tracker:FindObjectForCode("manual_location_storage").ItemState
    end
    -- repeat that here for every cache-storage item you create just to be save
    
    preOnClear()
    
    ScriptHost:RemoveWatchForCode("StateChanged")
    ScriptHost:RemoveOnLocationSectionHandler("location_section_change_handler")
    --SLOT_DATA = slot_data
    CUR_INDEX = -1
    -- reset locations
    for _, location_array in pairs(LOCATION_MAPPING) do
        for _, location in pairs(location_array) do
            if location then
                local location_obj = Tracker:FindObjectForCode(location)
                if location_obj then
                    if location:sub(1, 1) == "@" then
                        if custom_storage_item.MANUAL_LOCATIONS[ROOM_SEED][location_obj.FullID] then
                            location_obj.AvailableChestCount = custom_storage_item.MANUAL_LOCATIONS[ROOM_SEED][location_obj.FullID]
                        else
                            location_obj.AvailableChestCount = location_obj.ChestCount
                        end
                    else
                        location_obj.Active = false
                    end
                end
            end
        end
    end
    -- reset items
    for _, item_array in pairs(ITEM_MAPPING) do
        for _, item_pair in pairs(item_array) do
            item_code = item_pair[1]
            item_type = item_pair[2]
            -- print("on clear", item_code, item_type)
            local item_obj = Tracker:FindObjectForCode(item_code)
            if item_obj then
                if item_obj.Type == "toggle" then
                    item_obj.Active = false
                elseif item_obj.Type == "progressive" then
                    item_obj.CurrentStage = 0
                elseif item_obj.Type == "consumable" then
                    if item_obj.MinCount then
                        item_obj.AcquiredCount = item_obj.MinCount
                    else
                        item_obj.AcquiredCount = 0
                    end
                elseif item_obj.Type == "progressive_toggle" then
                    item_obj.CurrentStage = 0
                    item_obj.Active = false
                end
            end
        end
    end
    PLAYER_ID = Archipelago.PlayerNumber or -1
    TEAM_NUMBER = Archipelago.TeamNumber or 0
    SLOT_DATA = slot_data
    applyProgressionSettings(slot_data)
    -- if Tracker:FindObjectForCode("autofill_settings").Active == true then
    --     autoFill(slot_data)
    -- end
    -- print(PLAYER_ID, TEAM_NUMBER)
    if Archipelago.PlayerNumber > -1 then
        if #ALL_LOCATIONS > 0 then
            ALL_LOCATIONS = {}
        end
        for _, value in pairs(Archipelago.MissingLocations) do
            table.insert(ALL_LOCATIONS, #ALL_LOCATIONS + 1, value)
        end

        for _, value in pairs(Archipelago.CheckedLocations) do
            table.insert(ALL_LOCATIONS, #ALL_LOCATIONS + 1, value)
        end

        HINTS_ID = "_read_hints_"..TEAM_NUMBER.."_"..PLAYER_ID
        Archipelago:SetNotify({HINTS_ID})
        Archipelago:Get({HINTS_ID})
    end
    UpdateFillCounters()
    ScriptHost:AddOnFrameHandler("load handler", OnFrameHandler)
    MANUAL_CHECKED = true
end

function onItem(index, item_id, item_name, player_number)
    if index <= CUR_INDEX then
        return
    end
    local is_local = player_number == Archipelago.PlayerNumber
    CUR_INDEX = index;
    local item = ITEM_MAPPING[item_id]
    if not item or not item[1] then
        --print(string.format("onItem: could not find item mapping for id %s", item_id))
        return
    end
    for _, item_pair in pairs(item) do
        item_code = item_pair[1]
        item_type = item_pair[2]
        local item_obj = Tracker:FindObjectForCode(item_code)
        if item_obj then
            if item_obj.Type == "toggle" then
                -- print("toggle")
                item_obj.Active = true
            elseif item_obj.Type == "progressive" then
                -- print("progressive")
                if item_obj.Active == true then
                    item_obj.CurrentStage = item_obj.CurrentStage + 1
                else
                    item_obj.Active = true
                end
            elseif item_obj.Type == "consumable" then
                -- print("consumable")
                item_obj.AcquiredCount = item_obj.AcquiredCount + item_obj.Increment * (tonumber(item_pair[3]) or 1)
            elseif item_obj.Type == "progressive_toggle" then
                -- print("progressive_toggle")
                if item_obj.Active then
                    item_obj.CurrentStage = item_obj.CurrentStage + 1
                else
                    item_obj.Active = true
                end
            end
        else
            print(string.format("onItem: could not find object for code %s", item_code[1]))
        end
    end
end

--called when a location gets cleared
function onLocation(location_id, location_name)
    MANUAL_CHECKED = false
    local location_array = LOCATION_MAPPING[location_id]
    if not location_array or not location_array[1] then
        print(string.format("onLocation: could not find location mapping for id %s", location_id))
        return
    end

    for _, location in pairs(location_array) do
        local location_obj = Tracker:FindObjectForCode(location)
        -- print(location, location_obj)
        if location_obj then
            if location:sub(1, 1) == "@" then
                location_obj.AvailableChestCount = location_obj.AvailableChestCount - 1
            else
                location_obj.Active = true
            end
        else
            print(string.format("onLocation: could not find location_object for code %s", location))
        end
    end
    UpdateFillCounters()
    MANUAL_CHECKED = true
end

-- this Autofill function is meant as an example on how to do the reading from slotdata and mapping the values to 
-- your own settings
-- function autoFill()
--     if SLOT_DATA == nil  then
--         print("its fucked")
--         return
--     end
--     -- print(dump_table(SLOT_DATA))

--     mapToggle={[0]=0,[1]=1,[2]=1,[3]=1,[4]=1}
--     mapToggleReverse={[0]=1,[1]=0,[2]=0,[3]=0,[4]=0}
--     mapTripleReverse={[0]=2,[1]=1,[2]=0}

--     slotCodes = {
--         map_name = {code="", mapping=mapToggle...}
--     }
--     -- print(dump_table(SLOT_DATA))
--     -- print(Tracker:FindObjectForCode("autofill_settings").Active)
--     if Tracker:FindObjectForCode("autofill_settings").Active == true then
--         for settings_name , settings_value in pairs(SLOT_DATA) do
--             -- print(k, v)
--             if slotCodes[settings_name] then
--                 item = Tracker:FindObjectForCode(slotCodes[settings_name].code)
--                 if item.Type == "toggle" then
--                     item.Active = slotCodes[settings_name].mapping[settings_value]
--                 else 
--                     -- print(k,v,Tracker:FindObjectForCode(slotCodes[k].code).CurrentStage, slotCodes[k].mapping[v])
--                     item.CurrentStage = slotCodes[settings_name].mapping[settings_value]
--                 end
--             end
--         end
--     end
-- end

function OnNotify(key, value, old_value)
    print("OnNotify", key, value, old_value)
    if value ~= old_value and key == HINTS_ID then
        Tracker.BulkUpdate = true
        for _, hint in ipairs(value) do
            if hint.finding_player == Archipelago.PlayerNumber then
                if hint.status == 0 then
                    UpdateHints(hint.location, 100+hint.item_flags)
                else
                    UpdateHints(hint.location, hint.status)
                end
            end
        end
        Tracker.BulkUpdate = false
    end
end

function OnNotifyLaunch(key, value)
    if key == HINTS_ID then
        Tracker.BulkUpdate = true
        for _, hint in ipairs(value) do
            if hint.finding_player == Archipelago.PlayerNumber then
                if hint.status == 0 then
                    UpdateHints(hint.location, 100+hint.item_flags)
                else
                    UpdateHints(hint.location, hint.status)
                end
            end
        end
        Tracker.BulkUpdate = false
    end
end

function UpdateHints(locationID, status) -->
    if Highlight then
        -- print(locationID, status)
        local location_table = LOCATION_MAPPING[locationID]
        for _, location in ipairs(location_table) do
            if location:sub(1, 1) == "@" then
                local obj = Tracker:FindObjectForCode(location)

                if obj then
                    if TROLL_PLAYER and HIGHLIGHT_LEVEL[status] == Highlight.Avoid then
                        obj.Highlight = HIGHLIGHT_LEVEL[30]
                    else
                        obj.Highlight = HIGHLIGHT_LEVEL[status]
                    end
                else
                    print(string.format("No object found for code: %s", location))
                end
            end
        end
    end
end


-- ScriptHost:AddWatchForCode("settings autofill handler", "autofill_settings", autoFill)
-- Archipelago:AddClearHandler("clear handler", onClearHandler)
-- Archipelago:AddItemHandler("item handler", onItem)
-- Archipelago:AddLocationHandler("location handler", onLocation)

-- Archipelago:AddSetReplyHandler("notify handler", OnNotify)
-- Archipelago:AddRetrievedHandler("notify launch handler", OnNotifyLaunch)



--doc
--hint layout
-- {
--     ["receiving_player"] = 1,
--     ["class"] = Hint,
--     ["finding_player"] = 1,
--     ["location"] = 67361,
--     ["found"] = false,
--     ["item_flags"] = 2, --bitflag --> 0=filler, 1=progression, 2=useful, 4=trap
--     ["status"] = 40, --bitflag --> 0=Unspecified, 10=NoPriority, 20=Avoid, 30=Priority, 40=None
--     ["entrance"] = ,
--     ["item"] = 66062,
-- } 

-- Progression settings from slot data
function applyProgressionSettings(slot_data)
    local settings = {
        "air_ride_progression_time_attack",
        "air_ride_progression_free_run",
        "air_ride_progression_high_effort",
        "city_trial_progression_free_run",
        "city_trial_progression_multiplayer",
        "city_trial_progression_rng",
        "city_trial_progression_bust_vehicles",
        "city_trial_progression_high_effort",
        "top_ride_progression_time_attack",
        "top_ride_progression_free_run",
        "top_ride_progression_high_effort",
        "top_ride_progression_multiplayer",
    }
    for _, code in ipairs(settings) do
        local item = Tracker:FindObjectForCode(code)
        if item then
            local val = slot_data[code]
            if val ~= nil then
                item.Active = (val == 1)
            end
        end
    end

    -- Utility toggles (death_link, energy_link, trap_link). These come from the YAML as
    -- booleans in slot_data; light up the icon when enabled, leave grey otherwise.
    local utility = { "death_link", "energy_link", "trap_link" }
    for _, code in ipairs(utility) do
        local item = Tracker:FindObjectForCode(code)
        if item then
            local val = slot_data[code]
            if val ~= nil then
                -- accept either bool or 0/1 from slot data
                if type(val) == "boolean" then
                    item.Active = val
                else
                    item.Active = (val == 1 or val == "1" or val == true)
                end
            end
        end
    end

    -- Seed Settings indicators: light an icon for each randomized (gated) category.
    -- slot_data flag -> tracker setting code.
    local gated = {
        ["machines_gated"]            = "progression_machines",
        ["abilities_gated"]           = "progression_abilities",
        ["base_abilities_gated"]      = "progression_base_abilities",
        ["colors_gated"]              = "progression_colors",
        ["city_trial_stadiums_gated"] = "progression_stadiums",
        ["city_trial_patches_gated"]  = "progression_patches",
        ["city_trial_boxes_gated"]    = "progression_boxes",
        ["city_trial_events_gated"]   = "progression_events",
        ["city_trial_items_gated"]    = "progression_ct_items",
        ["air_ride_courses_gated"]    = "progression_ar_courses",
        ["top_ride_courses_gated"]    = "progression_tr_courses",
        ["top_ride_items_gated"]      = "progression_tr_items",
        ["checklist_rewards_gated"]   = "progression_rewards",
    }
    for flag, code in pairs(gated) do
        local item = Tracker:FindObjectForCode(code)
        if item then
            local val = slot_data[flag]
            if type(val) == "boolean" then
                item.Active = val
            else
                item.Active = (val == 1 or val == "1" or val == true)
            end
        end
    end

    -- Top Ride control machines (Free Star / Steer Star). When machines are NOT gated, every machine
    -- is unlocked in-game from the start, but the multiworld sends no machine items, so nothing would
    -- light these up. Force both on in that case. When machines ARE gated, leave them to onItem: the
    -- game grants one guaranteed Top Ride starter (a precollected item) that lights itself up, and the
    -- other must be found. Runs after onClear's item-reset pass, so the forced-on state survives.
    -- Only ever light these from a LIVE room connection. The file-scope applyProgressionSettings(SLOT_DATA)
    -- call below runs on every load with empty slot data and no connection; without this guard, an absent
    -- machines_gated would read as "not gated" and wrongly light them before connecting.
    local connected = (Archipelago.PlayerNumber ~= nil and Archipelago.PlayerNumber > -1)
    local mg = slot_data["machines_gated"]
    local machines_gated_on = (mg == true or mg == 1 or mg == "1")
    if connected and not machines_gated_on then
        for _, code in ipairs(TR_CONTROL_MACHINES) do
            local item = Tracker:FindObjectForCode(code)
            if item then
                item.Active = true
            end
        end
    end

end

-- Grey out the Top Ride control machines when there is no live room connection. They should only
-- light from a room's settings (applyProgressionSettings) or a received starter item, never from
-- restored save state while disconnected. Registered as a one-shot frame handler below, so it runs
-- once after load + state-restore. The connection check (not a load flag) makes it race-proof: if
-- auto-connect already fired, it sees "connected" and leaves onClear/onItem-managed state alone.
function GreyTopRideMachinesIfDisconnected()
    if Archipelago.PlayerNumber and Archipelago.PlayerNumber > -1 then
        return
    end
    for _, code in ipairs(TR_CONTROL_MACHINES) do
        local item = Tracker:FindObjectForCode(code)
        if item then
            item.Active = false
        end
    end
end

-- Hook into slot data received
if SLOT_DATA ~= nil then
    applyProgressionSettings(SLOT_DATA)
end

-- One-shot: after the pack loads and PopTracker restores saved state, grey the Top Ride control
-- machines unless a live connection is already active. On connect, onClear re-lights them per the
-- room's settings; while disconnected they stay grey instead of showing stale restored state.
function GreyTRMachinesOnLoadHandler()
    ScriptHost:RemoveOnFrameHandler("KAR grey TR machines on load")
    GreyTopRideMachinesIfDisconnected()
end
ScriptHost:AddOnFrameHandler("KAR grey TR machines on load", GreyTRMachinesOnLoadHandler)
