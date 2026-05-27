
ACCESS_NONE = AccessibilityLevel.None
ACCESS_PARTIAL = AccessibilityLevel.Partial
ACCESS_INSPECT = AccessibilityLevel.Inspect
ACCESS_SEQUENCEBREAK = AccessibilityLevel.SequenceBreak
ACCESS_NORMAL = AccessibilityLevel.Normal
ACCESS_CLEARED = AccessibilityLevel.Cleared

local bool_to_accesslvl = {
    [true] = ACCESS_NORMAL,
    [false] = ACCESS_NONE
}
                
function A(result)
    if result then
        return ACCESS_NORMAL
    end
    return ACCESS_NONE
end

function ALL(...)
    local args = { ... }
    local min = ACCESS_NORMAL
    for _, v in ipairs(args) do
        if type(v) == "function" then
            v = v()
        elseif type(v) == "string" then
            v = HAS(v)
        end
        if type(v) == "boolean" then
            v = bool_to_accesslvl[v]
        end
        if v < min then
            if v == ACCESS_NONE then
                return ACCESS_NONE
            end
            min = v
        end
    end
    return min
end

function ANY(...)
    local args = { ... }
    local max = ACCESS_NONE
    for _, v in ipairs(args) do
        if type(v) == "function" then
            v = v()
        elseif type(v) == "string" then
            v = HAS(v)
        end
        if type(v) == "boolean" then
            v = bool_to_accesslvl[v]
            -- v = A(v)
        end
        if v > max then
            if v == ACCESS_NORMAL then
                return ACCESS_NORMAL
            end
            max = v
        end
    end
    return max
end

function HAS(item, amount, amountInLogic)
    local count = Tracker:ProviderCountForCode(item)

    -- print(item, count, amount, amountInLogic)
    if amountInLogic then
        if count >= amountInLogic then
            return ACCESS_NORMAL
        elseif count >= amount then
            return ACCESS_SEQUENCEBREAK
        end
        return ACCESS_NONE
    end
    if not amount then
        if count > 0 then
            return ACCESS_NORMAL
        end
        return ACCESS_NONE
    else
        if count >= amount then
            return ACCESS_SEQUENCEBREAK
        end
        return ACCESS_NONE
    end
end


-- ANY function added here and used in access rules should try to return an Accessibility Level if it is used inside
-- the ANY() and ALL() functions
--
--

STADIUM_CODES = {
    "stadium_drag_race_1", "stadium_drag_race_2", "stadium_drag_race_3", "stadium_drag_race_4",
    "stadium_high_jump", "stadium_target_flight", "stadium_air_glider",
    "stadium_destruction_derby_1", "stadium_destruction_derby_2", "stadium_destruction_derby_3",
    "stadium_destruction_derby_4", "stadium_destruction_derby_5",
    "stadium_kirby_melee_1", "stadium_kirby_melee_2",
    "stadium_single_race_1", "stadium_single_race_2", "stadium_single_race_3",
    "stadium_single_race_4", "stadium_single_race_5", "stadium_single_race_6",
    "stadium_single_race_7", "stadium_single_race_8", "stadium_single_race_9",
    "stadium_vs_king_dedede"
}

-- Returns ACCESS_NORMAL if at least N stadium unlock items are owned, else ACCESS_NONE.
-- Usage in access_rules:  "$STADIUMS_AT_LEAST|10"
function STADIUMS_AT_LEAST(n)
    n = tonumber(n) or 0
    local count = 0
    for _, code in ipairs(STADIUM_CODES) do
        count = count + (Tracker:ProviderCountForCode(code) or 0)
    end
    if count >= n then
        return ACCESS_NORMAL
    end
    return ACCESS_NONE
end