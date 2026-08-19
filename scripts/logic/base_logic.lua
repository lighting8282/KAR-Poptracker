
-- this is the file to put all your custom logic functions into.
-- if you dont want to use the json based logic you can switch to a graph-based logic method.
-- the needed functions for that are in `/scripts/logic/graph_logic/logic_main.lua`.

-- Gated-category reachability.
-- Usage in access_rules: "$GATED|<setting_code>|<unlock_code>"
--   e.g. "$GATED|progression_tr_courses|map_top_ride_grass"
-- Returns NORMAL when the category is NOT gated this seed (Seed Settings indicator off), so
-- checks stay reachable when everything is available from the start. When the category IS gated,
-- the check is reachable only once its unlock item is held.
function GATED(setting_code, unlock_code)
    if Tracker:ProviderCountForCode(setting_code) == 0 then
        return ACCESS_NORMAL
    end
    return HAS(unlock_code)
end

-- Gated "any-of" reachability. Like GATED, but reachable once ANY one of the listed unlock codes is
-- held (mirrors the apworld's HasAny(box unlocks) rule for the box-break checklist cells). Returns
-- NORMAL when the category is not gated this seed.
-- Usage: "$GATED_ANY|progression_boxes|box_red|box_green|box_blue"
function GATED_ANY(setting_code, ...)
    if Tracker:ProviderCountForCode(setting_code) == 0 then
        return ACCESS_NORMAL
    end
    for _, code in ipairs({...}) do
        if Tracker:ProviderCountForCode(code) > 0 then
            return ACCESS_NORMAL
        end
    end
    return ACCESS_NONE
end

-- Gated "all-of" reachability. Reachable only once EVERY listed unlock code is held (HasAll), or
-- always when the category is not gated this seed. Used where the apworld requires several unlocks of
-- the SAME category (bust X while riding Y -> both machines; complete Dragoon+Hydra -> all 6 parts;
-- "race all courses" -> every course). One function call instead of chaining identical $GATED terms.
-- Usage: "$GATED_ALL|progression_machines|machine_wheelie_bike|machine_warp_star"
function GATED_ALL(setting_code, ...)
    if Tracker:ProviderCountForCode(setting_code) == 0 then
        return ACCESS_NORMAL
    end
    for _, code in ipairs({...}) do
        if Tracker:ProviderCountForCode(code) == 0 then
            return ACCESS_NONE
        end
    end
    return ACCESS_NORMAL
end

-- Item-pickup count cells ("get / pick up N items"). The in-game counter advances for any counting
-- item type. Those types are locked across THREE gates -- CT items, patches and abilities. Only when
-- ALL THREE are gated does nothing count until one such unlock is held; if any of the three gates is
-- off, that category's items always spawn so a counting item is always available. Mirrors the
-- apworld's _ITEM_PICKUP_LOCATIONS rule (HasAny over CT item + patch + ability unlocks). Boxes are
-- intentionally excluded -- breaking a box does not advance the counter.
-- Usage: "$CT_PICKUP_ANY"
local CT_COUNTING_ITEMS = {
    "ability_bomb", "ability_fire", "ability_freeze", "ability_mike", "ability_needle",
    "ability_plasma", "ability_sleep", "ability_sword", "ability_tornado", "ability_wheel",
    "ability_wing", "all_up", "food_apple", "food_curry", "food_energy_drink", "food_hamburger",
    "food_hotdog", "food_ice_cream_cone", "food_maxim_tomato", "food_omelet", "food_ramen",
    "food_rice_ball", "food_roast_chicken", "food_sushi", "part_dragoon_a", "part_dragoon_b",
    "part_dragoon_c", "part_hydra_x", "part_hydra_y", "part_hydra_z", "patch_unlock_boost",
    "patch_unlock_charge", "patch_unlock_defense", "patch_unlock_glide", "patch_unlock_hp",
    "patch_unlock_offense", "patch_unlock_top_speed", "patch_unlock_turn", "patch_unlock_weight",
    "special_offense_attack_up", "special_offense_candy", "special_offense_defense_up",
    "special_offense_fireworks", "special_offense_gold_spike", "special_offense_no_charge",
    "special_offense_panic_spin", "special_offense_run_amok", "special_offense_sensor_bomb",
    "special_offense_speed_up",
}
function CT_PICKUP_ANY()
    if Tracker:ProviderCountForCode("progression_ct_items") == 0
        or Tracker:ProviderCountForCode("progression_patches") == 0
        or Tracker:ProviderCountForCode("progression_abilities") == 0 then
        return ACCESS_NORMAL
    end
    for _, code in ipairs(CT_COUNTING_ITEMS) do
        if Tracker:ProviderCountForCode(code) > 0 then
            return ACCESS_NORMAL
        end
    end
    return ACCESS_NONE
end

-- Top Ride "collect N items" / "same item 3x in one race" cells. They need SOME Top Ride item type
-- able to spawn. The apworld builds this from every TR item unlock, plus the ability-themed keys when
-- abilities are gated, and applies it whenever top_ride_items_gated is on. Ability codes are listed
-- unconditionally here: if abilities are not gated no ability unlock items exist, so those entries
-- simply never match. (Step-boom and Who?-Paint have no tracker code yet and are omitted.)
-- Usage: "$TR_ITEM_ANY"
local TR_COUNTING_ITEMS = {
    "top_ride_item_big_cake", "top_ride_item_bomb", "top_ride_item_buzz_saw", "top_ride_item_charge_up",
    "top_ride_item_chickie", "top_ride_item_drill", "top_ride_item_fire", "top_ride_item_freeze_fan",
    "top_ride_item_hammer", "top_ride_item_invincible_candy", "top_ride_item_krako",
    "top_ride_item_lantern", "top_ride_item_mike", "top_ride_item_missile", "top_ride_item_party_ball",
    "top_ride_item_smokescreen", "top_ride_item_speed_down", "top_ride_item_speed_up",
    "top_ride_item_spinner",
    "ability_freeze", "ability_fire", "ability_bomb", "ability_mike",
}
function TR_ITEM_ANY()
    if Tracker:ProviderCountForCode("progression_tr_items") == 0 then
        return ACCESS_NORMAL
    end
    for _, code in ipairs(TR_COUNTING_ITEMS) do
        if Tracker:ProviderCountForCode(code) > 0 then
            return ACCESS_NORMAL
        end
    end
    return ACCESS_NONE
end

-- "Fill in over 100 Checklist blocks!" gate. The autotracker keeps a fill_count_<mode> consumable
-- equal to the number of checked boxes in that mode (Stadium counts toward City Trial). Reachable once
-- that count reaches n (use 99 -> "in logic once 99 boxes are filled"). Note: this counts completed
-- CHECKS only, not checkbox-filler/reward items (the tracker can't see those), so it trips late on
-- filler-heavy seeds.
-- Usage: "$FILL_AT_LEAST|fill_count_ct|99"
function FILL_AT_LEAST(count_code, n)
    n = tonumber(n) or 0
    if Tracker:ProviderCountForCode(count_code) >= n then
        return ACCESS_NORMAL
    end
    return ACCESS_NONE
end

-- function <name> (<parameters if needed>)
--     <actual code>
--     <indentations are just for readability>
-- end
--
                