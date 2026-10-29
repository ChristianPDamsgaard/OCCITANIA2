# Byzantine Empire (X09) focus tree: the Gabras emperors of Sinop and the march on Constantinople.
# Lore (from Christian): Emperor Guillen III of Aragon led a rogue Third Crusade that destroyed the old empire;
# the Latin Empire that followed collapsed when the Cumans sacked Constantinople and left it an ash heap.
# In the 1600s an ambitious Ilkhanid general rebelled against his liege during an Aragon-Ilkhanate war and
# founded the present Byzantine Empire, which has swapped sides between Aragon and the Ilkhanate ever since.
import sys, os
REPO = sys.argv[1]
J = lambda *p: os.path.join(REPO, *p)

F = []
def focus(id, x, y, icon, name, desc, cost=10, pre=None, excl=None, avail=None, bypass=None, effect="", ai=1, filters=None):
    F.append(dict(id=id, x=x, y=y, icon=icon, name=name, desc=desc, cost=cost, pre=pre or [], excl=excl or [],
                  avail=avail, bypass=bypass, effect=effect, ai=ai, filters=filters or []))

def build(state, btype, level, slots=0):
    s = f"if = {{ limit = {{ {state} = {{ is_owned_and_controlled_by = ROOT }} }}\n\t{state} = {{\n"
    if slots: s += f"\t\tadd_extra_state_shared_building_slots = {slots}\n"
    s += f"\t\tadd_building_construction = {{ type = {btype} level = {level} instant_build = yes }}\n\t}}\n}}\n"
    return s
def bunker(state, btype, level, sel):
    return (f"if = {{ limit = {{ {state} = {{ is_owned_and_controlled_by = ROOT }} }}\n"
            f"\t{state} = {{ add_building_construction = {{ type = {btype} level = {level} "
            f"province = {{ all_provinces = yes {sel} = yes }} instant_build = yes }} }}\n}}\n")
def tech(name, cat, bonus=0.5, uses=1):
    if cat.endswith("_doctrine"):
        return f"add_doctrine_cost_reduction = {{ name = {name} cost_reduction = 0.4 uses = {uses} category = {cat} }}\n"
    return f"add_tech_bonus = {{ name = {name} bonus = {bonus} uses = {uses} category = {cat} }}\n"
def leader(char):
    return f"recruit_character = {char}\npromote_character = {char}\n"
def claims(*states):
    return "".join(f"add_state_claim = {s}\n" for s in states)

CONSTANTINOPLE = 52   # Aragonese Thrace (Constantinople, VP province 9833)
BITHYNIA = [755, 754] # Bolu, Izmit (Bithynia, BTH: the Anatolian Cumans)
IONIA = [53, 54]      # Hudavendigar (Bursa), Aydin (Smyrna) - Aragonese, Byzantine cores
HELLAS = [49, 50, 62, 70, 99, 100, 329]

# ================= core =================
focus("X09_the_throne_of_sinop", 12, 0, "GFX_goal_generic_national_unity", "The Throne of Sinop",
      "Emperor Tiberios V Gabras rules the Romans from a Black Sea harbour town, in a palace that was once an Ilkhanid governor's residence. His empire is small, poor and surrounded. It is also the only Roman Empire left.",
      cost=5, effect="add_political_power = 75\nadd_stability = 0.05\n", ai=50, filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_legacy_of_gabras", 12, 1, "GFX_focus_hun_elect_a_king", "The Legacy of Theodoros Gabras",
      "Three centuries ago Theodoros Gabras, a Greek general in the service of the Ilkhan, turned his army around in the middle of a war with Aragon and crowned himself Emperor of the Romans. Every Byzantine schoolchild knows the story; every Byzantine diplomat knows its lesson.",
      pre=[["X09_the_throne_of_sinop"]], effect="add_political_power = 50\nadd_war_support = 0.05\n",
      ai=20, filters=["FOCUS_FILTER_POLITICAL"])

# ---------------- church and succession ----------------
focus("X09_the_patriarch_in_exile", 10, 2, "GFX_goal_generic_propaganda", "The Patriarch in Exile",
      "The Ecumenical Patriarch has not seen Constantinople since the Cumans burned it. His throne stands in a side chapel in Sinop, facing west, waiting.",
      pre=[["X09_legacy_of_gabras"]], effect="add_stability = 0.05\nadd_war_support = 0.05\n",
      filters=["FOCUS_FILTER_STABILITY"])
focus("X09_the_purple_chamber", 12, 2, "GFX_goal_generic_political_pressure", "The Purple Chamber",
      "Tiberios V is seventy-three. His son Michael was born in the purple; the Megas Domestikos commands the army; and the old senatorial families have started meeting again. Byzantium has always settled its successions with daggers. Perhaps not this time.",
      pre=[["X09_legacy_of_gabras"]], effect="add_political_power = 50\n", filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_the_porphyrogennetos", 10, 3, "GFX_focus_rom_royal_dictatorship", "The Porphyrogennetos",
      "Tiberios crowns his son co-emperor and retires to a monastery on the Halys. Michael VI Gabras is young, learned and in a hurry to rebuild the empire.",
      pre=[["X09_the_purple_chamber"]], excl=["X09_the_megas_domestikos", "X09_the_senate_of_new_rome"],
      effect=leader("X09_michael_gabras") + "add_ideas = X09_reforming_autocrat\nadd_stability = 0.05\n",
      ai=5, filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_the_megas_domestikos", 12, 3, "GFX_goal_generic_army_doctrines", "The Megas Domestikos",
      "Nikephoros Vranas has commanded the imperial army for twenty years. When the old emperor dies, the tagmata salute him in the Hippodrome of Sinop. He keeps the title of Domestikos; everyone knows who rules.",
      pre=[["X09_the_purple_chamber"]], excl=["X09_the_porphyrogennetos", "X09_the_senate_of_new_rome"],
      effect=leader("X09_nikephoros_vranas") + "add_ideas = X09_rule_of_the_tagmata\n",
      ai=3, filters=["FOCUS_FILTER_POLITICAL", "FOCUS_FILTER_WAR_SUPPORT"])
focus("X09_the_senate_of_new_rome", 14, 3, "GFX_goal_support_democracy", "The Senate of New Rome",
      "The Senate of the Romans is older than any king in Europe. The senatorial families force the dying emperor to sign a charter: the Senate will choose the government, and the emperor will reign.",
      pre=[["X09_the_purple_chamber"]], excl=["X09_the_porphyrogennetos", "X09_the_megas_domestikos"],
      effect=("set_politics = { ruling_party = democratic elections_allowed = yes last_election = \"1936.1.1\" election_frequency = 48 }\n"
              "set_popularities = { democratic = 55 absolutist = 40 fascism = 5 }\n"
              + leader("X09_konstantinos_laskaris") + "add_ideas = X09_senatorial_charter\n"),
      ai=2, filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_curb_the_dynatoi", 10, 4, "GFX_goal_generic_political_pressure", "Curb the Dynatoi",
      "The great landowners of Cappadocia have grown fat while the soldier-farmers who defend the frontiers starve. Michael VI will break them, as Basil II once did.",
      pre=[["X09_the_porphyrogennetos"]], effect="add_political_power = 100\nadd_manpower = 10000\n",
      filters=["FOCUS_FILTER_POLITICAL", "FOCUS_FILTER_MANPOWER"])
focus("X09_the_tagmata_rule", 12, 4, "GFX_goal_generic_position_armies", "The Tagmata Rule",
      "Every governor is an officer, every officer a loyal man of the Domestikos, and every Roman a soldier in waiting.",
      pre=[["X09_the_megas_domestikos"]], effect="army_experience = 25\nadd_war_support = 0.05\n",
      filters=["FOCUS_FILTER_ARMY_XP", "FOCUS_FILTER_WAR_SUPPORT"])
focus("X09_the_senate_charters", 14, 4, "GFX_focus_generic_treaty", "The Charters of the Senate",
      "Written law, appointed judges and a treasury that answers to the Senate. Byzantine bureaucracy, for once, will work for the Romans instead of on them.",
      pre=[["X09_the_senate_of_new_rome"]], effect="add_stability = 0.1\nadd_political_power = 50\n",
      filters=["FOCUS_FILTER_STABILITY"])
focus("X09_the_basileia_endures", 12, 5, "GFX_goal_generic_national_unity", "The Basileia Endures",
      "Emperors die, generals fall and senates argue, but the Basileia of the Romans endures. It has survived crusaders, Cumans and khans. It will survive this century.",
      pre=[["X09_curb_the_dynatoi", "X09_the_tagmata_rule", "X09_the_senate_charters"]],
      effect="add_stability = 0.1\nadd_war_support = 0.05\n", filters=["FOCUS_FILTER_STABILITY"])

# ---------------- between Aragon and the Ilkhan ----------------
focus("X09_between_lion_and_khan", 18, 1, "GFX_goal_generic_neutrality_focus", "Between Lion and Khan",
      "For three hundred years Byzantium has survived by changing sides between the Lion of Aragon and the Ilkhan in Tabriz, usually in the middle of a war. Each of them hates us. Each of them needs us. The emperor must choose again.",
      pre=[["X09_the_throne_of_sinop"]], effect="add_political_power = 50\n", ai=20, filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_aragons_shield", 16, 2, "GFX_focus_generic_treaty", "Aragon's Shield",
      "Aragon is the stronger, and its enemies are in the west. We will hold the eastern frontier for Saragossa, and Saragossa will look the other way while we take back Trebizond.",
      pre=[["X09_between_lion_and_khan"]], excl=["X09_return_to_the_khan", "X09_neither_latin_nor_mongol"],
      avail="country_exists = SPC\nNOT = { has_war_with = SPC }",
      effect=("add_opinion_modifier = { target = SPC modifier = positive_50 }\n"
              "SPC = { add_opinion_modifier = { target = ROOT modifier = positive_50 } }\n"
              "diplomatic_relation = { country = SPC relation = non_aggression_pact }\n"),
      ai=2, filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_return_to_the_khan", 18, 2, "GFX_focus_generic_treaty", "Return to the Khan",
      "Gabras rebelled against the Ilkhan, but the Ilkhan was the only one who never tried to burn our churches. Tabriz will gladly arm anyone who marches on Aragonese Constantinople.",
      pre=[["X09_between_lion_and_khan"]], excl=["X09_aragons_shield", "X09_neither_latin_nor_mongol"],
      avail="country_exists = X63\nNOT = { has_war_with = X63 }",
      effect=("add_opinion_modifier = { target = X63 modifier = positive_50 }\n"
              "X63 = { add_opinion_modifier = { target = ROOT modifier = positive_50 } }\n"
              "diplomatic_relation = { country = X63 relation = non_aggression_pact }\n"),
      ai=3, filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_neither_latin_nor_mongol", 20, 2, "GFX_goal_generic_national_unity", "Neither Latin nor Mongol",
      "The Latins destroyed the old empire. The Mongols made us their soldiers. For once, Byzantium will be nobody's frontier but its own.",
      pre=[["X09_between_lion_and_khan"]], excl=["X09_aragons_shield", "X09_return_to_the_khan"],
      effect="add_ideas = X09_roman_pride\n", ai=4, filters=["FOCUS_FILTER_POLITICAL", "FOCUS_FILTER_STABILITY"])
focus("X09_the_eastern_marches", 16, 3, "GFX_goal_generic_more_territorial_claims", "The Eastern Marches",
      "Trebizond was a Roman city before there was a Khan. So were the fortresses of the upper Tigris and the island of Cyprus.",
      pre=[["X09_aragons_shield"]], effect=claims(768, 770, 767), filters=["FOCUS_FILTER_ANNEXATION"])
focus("X09_war_for_trebizond", 16, 4, "GFX_goal_generic_territory_or_war", "War for Trebizond",
      "With Aragonese rifles and Aragonese silence, the army marches east along the Pontic coast.",
      pre=[["X09_the_eastern_marches"]], avail="country_exists = X63\nNOT = { has_war_with = X63 }",
      effect="create_wargoal = { type = take_state_focus target = X63 generator = { 768 770 767 } }\n",
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("X09_trebizond_restored", 16, 5, "GFX_goal_generic_national_unity", "The Pontic Crown",
      "Trebizond is Roman again, and the emperor takes the old Pontic title of the Grand Komnenoi alongside his own.",
      pre=[["X09_war_for_trebizond"]], avail="owns_state = 768",
      effect="add_state_core = 768\nadd_stability = 0.05\nadd_political_power = 50\n", filters=["FOCUS_FILTER_STABILITY"])
focus("X09_the_khans_favour", 18, 3, "GFX_goal_generic_small_arms", "The Khan's Favour",
      "Ilkhanid caravans arrive in Sinop with rifles and shells. The Khan asks only one thing in return: that we point them west.",
      pre=[["X09_return_to_the_khan"]],
      effect=("add_equipment_to_stockpile = { type = infantry_equipment amount = 2000 producer = X63 }\n"
              "add_equipment_to_stockpile = { type = artillery_equipment amount = 48 producer = X63 }\n" + claims(*IONIA)),
      filters=["FOCUS_FILTER_MANPOWER", "FOCUS_FILTER_ANNEXATION"])
focus("X09_roman_pride", 20, 3, "GFX_goal_generic_propaganda", "The Romans Stand Alone",
      "Our soldiers will no longer carry Ilkhanid rifles or wear Aragonese boots. What Byzantium needs, Byzantium will make.",
      pre=[["X09_neither_latin_nor_mongol"]], effect="army_experience = 15\n" + claims(*IONIA),
      filters=["FOCUS_FILTER_ARMY_XP", "FOCUS_FILTER_ANNEXATION"])

# ---------------- the Greek question ----------------
focus("X09_the_greek_question", 24, 1, "GFX_goal_generic_political_pressure", "The Greek Question",
      "Across the Aegean, the Greeks of Hellas plot against Aragon. They speak our language and pray in our churches, but they call themselves Hellenes, not Romans, and they have a king of their own.",
      pre=[["X09_the_throne_of_sinop"]], effect="add_political_power = 25\n", ai=10, filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_brothers_in_orthodoxy", 23, 2, "GFX_focus_generic_treaty", "Brothers in Orthodoxy",
      "Hellene or Roman, we are one Orthodox people. A free Greece is a friend on Aragon's flank.",
      pre=[["X09_the_greek_question"]], excl=["X09_all_greeks_are_romans"],
      effect=("if = { limit = { country_exists = GRE }\n"
              "\tadd_opinion_modifier = { target = GRE modifier = positive_50 }\n"
              "\tGRE = { add_opinion_modifier = { target = ROOT modifier = positive_50 } }\n}\n"),
      ai=3, filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_all_greeks_are_romans", 25, 2, "GFX_goal_generic_more_territorial_claims", "All Greeks Are Romans",
      "There is no such thing as a Hellene. There are Romans who have forgotten it. Every Greek province belongs to the Basileia, and so does every Greek king.",
      pre=[["X09_the_greek_question"]], excl=["X09_brothers_in_orthodoxy"],
      effect=claims(*HELLAS) + "add_war_support = 0.05\n", ai=1, filters=["FOCUS_FILTER_ANNEXATION"])
focus("X09_arms_for_the_hetairists", 23, 3, "GFX_goal_generic_small_arms", "Arms for the Hetairists",
      "Rifles from the imperial arsenal cross the Aegean in fishing boats. If the Greeks rise, they will rise with Byzantine guns.",
      pre=[["X09_brothers_in_orthodoxy"]], avail="country_exists = GRE\nNOT = { has_war_with = GRE }",
      effect=("GRE = {\n\tadd_equipment_to_stockpile = { type = infantry_equipment amount = 1000 producer = X09 }\n"
              "\tadd_opinion_modifier = { target = ROOT modifier = positive_50 }\n}\nadd_political_power = -25\n"),
      filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_the_orthodox_league", 23, 4, "GFX_focus_generic_treaty", "The Orthodox League",
      "Sinop and the Greek crown sign a pact of mutual defence before the icon of the Hodegetria.",
      pre=[["X09_arms_for_the_hetairists"]], avail="country_exists = GRE\nNOT = { has_war_with = GRE }",
      effect=("if = { limit = { is_in_faction = no }\n\tcreate_faction_from_template = { template = faction_template_absolutist name = X09_orthodox_league }\n}\n"
              "if = { limit = { is_faction_leader = yes GRE = { is_in_faction = no } }\n\tadd_to_faction = GRE\n}\n"),
      filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_bring_the_hellenes_home", 25, 4, "GFX_goal_generic_territory_or_war", "Bring the Hellenes Home",
      "The Greek kingdom and the Athenian republic are children playing at statehood. The Basileia will take them under its wing, gently if possible.",
      pre=[["X09_all_greeks_are_romans"]], avail="OR = { country_exists = GRE country_exists = HEL }",
      effect=("if = { limit = { country_exists = GRE NOT = { has_war_with = GRE } } create_wargoal = { type = puppet_wargoal_focus target = GRE } }\n"
              "if = { limit = { country_exists = HEL NOT = { has_war_with = HEL } } create_wargoal = { type = annex_everything target = HEL } }\n"),
      filters=["FOCUS_FILTER_ANNEXATION"])

# ---------------- the march on Constantinople ----------------
focus("X09_the_ash_heap", 19, 5, "GFX_goal_generic_more_territorial_claims", "The Ash Heap of the Queen of Cities",
      "Guillen III's crusaders took Constantinople; the Cumans burned it. What remains is a ring of broken walls around an Aragonese garrison town, the shell of Hagia Sophia and a hundred thousand ghosts. It is still the City. There is only one.",
      pre=[["X09_the_khans_favour", "X09_roman_pride", "X09_stab_the_lion"]], effect=claims(CONSTANTINOPLE) + "add_war_support = 0.1\n",
      ai=30, filters=["FOCUS_FILTER_ANNEXATION", "FOCUS_FILTER_WAR_SUPPORT"])
focus("X09_avenge_the_sack", 18, 6, "GFX_goal_generic_territory_or_war", "Avenge the Sack",
      "The descendants of the Cumans who burned Constantinople still rule Bithynia from Bolu, astride the road to the Bosporus. The road will be cleared.",
      pre=[["X09_the_ash_heap"]], avail="country_exists = BTH\nNOT = { has_war_with = BTH }",
      effect=claims(*BITHYNIA) + "create_wargoal = { type = take_state_focus target = BTH generator = { 755 754 } }\n",
      ai=20, filters=["FOCUS_FILTER_ANNEXATION"])
focus("X09_strike_while_aragon_bleeds", 20, 6, "GFX_goal_generic_major_war", "Strike While Aragon Bleeds",
      "Aragon's garrisons are fighting Greek rebels in every valley from Florina to Sparta, or Occitan armies in the west. The Lion has turned its back. Now.",
      pre=[["X09_the_ash_heap"]],
      avail="country_exists = SPC\nNOT = { has_war_with = SPC }\nSPC = { has_war = yes }",
      effect="create_wargoal = { type = take_state_focus target = SPC generator = { 52 53 } }\nadd_war_support = 0.05\n",
      ai=30, filters=["FOCUS_FILTER_ANNEXATION"])
focus("X09_the_ionian_coast", 22, 7, "GFX_goal_generic_amphibious_assault", "The Ionian Coast",
      "Smyrna was Roman when Aragon was a goat pasture in the Pyrenees.",
      pre=[["X09_strike_while_aragon_bleeds"]], avail="country_exists = SPC\n54 = { is_owned_by = SPC }",
      effect="create_wargoal = { type = take_state_focus target = SPC generator = { 54 } }\n",
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("X09_enter_the_golden_gate", 19, 7, "GFX_goal_generic_occupy_states_ongoing_war", "Through the Golden Gate",
      "After six hundred years a Roman emperor rides through the Golden Gate. The streets are rubble and the crowds are small, but the bells of every surviving church ring at once.",
      pre=[["X09_avenge_the_sack", "X09_strike_while_aragon_bleeds"]], avail="owns_state = 52",
      effect=("add_state_core = 52\nset_capital = { state = 52 }\n"
              "add_victory_points = { province = 9833 value = 25 }\n"
              "add_stability = 0.1\nadd_war_support = 0.1\nadd_political_power = 100\n"
              "news_event = { id = byzantium.1 hours = 6 }\n"),
      ai=50, filters=["FOCUS_FILTER_STABILITY", "FOCUS_FILTER_ANNEXATION"])
focus("X09_rebuild_the_queen_of_cities", 18, 8, "GFX_goal_generic_construct_civ_factory", "Rebuild the Queen of Cities",
      "Families from Sinop, Trebizond and every Greek village of Anatolia stream into the empty quarters of the City.",
      pre=[["X09_enter_the_golden_gate"]],
      effect=build(52, "industrial_complex", 2, 2) + build(52, "infrastructure", 2) + "add_victory_points = { province = 9833 value = 15 }\n",
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("X09_hagia_sophia", 20, 8, "GFX_goal_generic_national_unity", "The Holy Wisdom",
      "The great dome survived the Cumans, blackened but standing. Masons and icon painters work through the winter to make it ready for Easter.",
      pre=[["X09_enter_the_golden_gate"]], effect="add_stability = 0.1\nadd_war_support = 0.05\n",
      filters=["FOCUS_FILTER_STABILITY"])
focus("X09_the_theodosian_walls", 18, 9, "GFX_goal_generic_fortify_city", "The Theodosian Walls",
      "The land walls held for a thousand years. With concrete and artillery, they will hold for another thousand.",
      pre=[["X09_rebuild_the_queen_of_cities"]],
      effect=bunker(52, "bunker", 3, "limit_to_border") + bunker(52, "coastal_bunker", 2, "limit_to_coastal"),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("X09_the_patriarch_returns", 20, 9, "GFX_goal_generic_propaganda", "The Patriarch Returns",
      "The Ecumenical Patriarch crosses the Bosporus with his throne, his relics and his choir. For the first time in six centuries he celebrates the liturgy in the Holy Wisdom.",
      pre=[["X09_hagia_sophia"], ["X09_the_patriarch_in_exile"]], effect="add_ideas = X09_ecumenical_throne\n",
      filters=["FOCUS_FILTER_STABILITY"])
focus("X09_emperor_of_the_romans", 19, 10, "GFX_focus_hun_elect_a_king", "Emperor of the Romans",
      "Crowned in the Holy Wisdom by the Ecumenical Patriarch, the emperor is no longer the Emperor in Sinop. He is the Emperor of the Romans, in New Rome, as God intended.",
      pre=[["X09_the_theodosian_walls"], ["X09_the_patriarch_returns"]],
      effect=("set_cosmetic_tag = X09_roman_empire\nadd_ideas = X09_new_rome\n"
              "every_owned_state = { limit = { OR = { state = 53 state = 54 state = 754 state = 755 } } add_core_of = ROOT }\n"),
      filters=["FOCUS_FILTER_STABILITY", "FOCUS_FILTER_ANNEXATION"])

# ================= economy (left) =================
focus("X09_the_pontic_economy", 2, 1, "GFX_goal_generic_trade", "The Pontic Economy",
      "Sinop lives on hazelnuts, timber, fish and the caravan trade from the east. It is not enough to build an empire on, yet.",
      pre=[["X09_the_throne_of_sinop"]], effect=build(96, "industrial_complex", 1, 1), filters=["FOCUS_FILTER_INDUSTRY"])
focus("X09_sinop_shipyards", 0, 2, "GFX_goal_generic_construct_naval_dockyard", "The Shipyards of Sinop",
      "Sinop built the galleys of the Pontic emperors. Its slipways can build destroyers.",
      pre=[["X09_the_pontic_economy"]], effect=build(96, "dockyard", 1, 1), filters=["FOCUS_FILTER_INDUSTRY"])
focus("X09_pontic_copper", 2, 2, "GFX_goal_generic_construct_military", "Copper and Chromium of Kastamonu",
      "The mountains of Paphlagonia are full of ore that nobody has bothered to dig.",
      pre=[["X09_the_pontic_economy"]],
      effect="if = { limit = { owns_state = 56 } add_resource = { type = chromium amount = 6 state = 56 } }\nif = { limit = { owns_state = 56 } add_resource = { type = steel amount = 4 state = 56 } }\n",
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("X09_cappadocian_granaries", 4, 2, "GFX_goal_generic_production", "The Cappadocian Granaries",
      "Behind every Roman army of the past stood the wheat of the Anatolian plateau.",
      pre=[["X09_the_pontic_economy"]], effect="add_stability = 0.05\n" + build(63, "industrial_complex", 1, 1),
      filters=["FOCUS_FILTER_INDUSTRY", "FOCUS_FILTER_STABILITY"])
focus("X09_the_black_sea_fleet", 0, 3, "GFX_goal_generic_build_navy", "The Black Sea Fleet",
      "Cuman pirates and Ilkhanid gunboats have ruled the Pontus for too long.",
      pre=[["X09_sinop_shipyards"]], effect="navy_experience = 25\n" + tech("X09_the_black_sea_fleet", "naval_doctrine", 0.5, 1) + "recruit_character = X09_alexios_notaras\n",
      filters=["FOCUS_FILTER_NAVY_XP", "FOCUS_FILTER_RESEARCH"])
focus("X09_anatolian_railways", 2, 3, "GFX_goal_generic_construct_infrastructure", "The Anatolian Railways",
      "A railway from Sinop to Ankara and Konya, and one day to the Bosporus.",
      pre=[["X09_pontic_copper"]], effect=build(96, "infrastructure", 1) + build(56, "infrastructure", 1) + build(63, "infrastructure", 1) + build(95, "infrastructure", 1),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("X09_the_imperial_arsenal", 4, 3, "GFX_goal_generic_construct_mil_factory", "The Imperial Arsenal",
      "The arsenal of Ankara will make Roman rifles, so that no khan or king can disarm us again.",
      pre=[["X09_cappadocian_granaries"]], effect=build(63, "arms_factory", 1, 1) + build(96, "arms_factory", 1, 1),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("X09_masters_of_the_bosporus", 0, 5, "GFX_goal_generic_navy_submarine", "Masters of the Bosporus",
      "Whoever holds the straits holds the Black Sea. Torpedo boats and submarines will make them ours.",
      pre=[["X09_the_black_sea_fleet"]], effect=tech("X09_masters_of_the_bosporus", "ss_tech", 0.5, 2) + "navy_experience = 15\n",
      filters=["FOCUS_FILTER_RESEARCH", "FOCUS_FILTER_NAVY_XP"])
focus("X09_the_silk_road_of_antioch", 4, 4, "GFX_goal_generic_trade", "The Silk Road of Antioch",
      "Antioch is the last Byzantine city on the old caravan road to Persia. Its customs house can still make the empire rich.",
      pre=[["X09_the_imperial_arsenal"]], avail="owns_state = 98",
      effect="add_political_power = 75\n" + build(98, "industrial_complex", 1, 1), filters=["FOCUS_FILTER_INDUSTRY"])
focus("X09_reform_the_themes", 2, 5, "GFX_goal_generic_construction2", "Reform the Themes",
      "The old theme system made every province a military district and every soldier a farmer. Modernised, it will give us an army and an administration in one.",
      pre=[["X09_anatolian_railways"], ["X09_the_imperial_arsenal"]], effect="add_ideas = X09_reformed_themes\n",
      filters=["FOCUS_FILTER_INDUSTRY", "FOCUS_FILTER_MANPOWER"])
focus("X09_the_golden_bezant", 2, 6, "GFX_goal_generic_production", "The Golden Bezant",
      "For seven centuries the bezant was the money of the world. A new gold-backed currency will make it so again, at least between Sinop and Antioch.",
      pre=[["X09_reform_the_themes"]], effect="add_ideas = X09_golden_bezant\n", filters=["FOCUS_FILTER_INDUSTRY"])

# ================= army =================
focus("X09_the_tagmata", 7, 1, "GFX_goal_generic_allies_build_infantry", "Raise the Tagmata",
      "The professional regiments of the capital, the tagmata, will be rebuilt as the core of a modern army.",
      pre=[["X09_the_throne_of_sinop"]], effect="army_experience = 15\n", filters=["FOCUS_FILTER_ARMY_XP"])
focus("X09_the_varangian_guard", 6, 2, "GFX_goal_generic_special_forces", "The Varangian Guard",
      "Scandinavian volunteers have served the emperors since the age of the Rus. Harald Eiriksson and his axemen, now riflemen, swear the old oath to the Basileus.",
      pre=[["X09_the_tagmata"]], effect="load_oob = \"X09_varangian_guard\"\nrecruit_character = X09_harald_eiriksson\n",
      filters=["FOCUS_FILTER_MANPOWER"])
focus("X09_the_akritai", 8, 2, "GFX_goal_generic_defence", "The Akritai",
      "The border lords of the east held the frontier against Arabs and Turks for centuries. Their heirs will hold it against the Ilkhan.",
      pre=[["X09_the_tagmata"]], effect=bunker(97, "bunker", 2, "limit_to_border") + bunker(98, "bunker", 2, "limit_to_border"),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("X09_greek_fire", 6, 3, "GFX_goal_generic_army_artillery", "Greek Fire",
      "The secret weapon of the old empire was a liquid fire nobody could put out. Its modern equivalents are artillery and flamethrowers.",
      pre=[["X09_the_varangian_guard"]], effect=tech("X09_greek_fire", "artillery", 0.5, 2), filters=["FOCUS_FILTER_RESEARCH"])
focus("X09_the_kataphraktoi", 8, 3, "GFX_goal_generic_build_tank", "The New Kataphraktoi",
      "Armoured horsemen once broke every army in Asia. Armoured cars and tanks will be their successors.",
      pre=[["X09_the_akritai"]], effect=tech("X09_the_kataphraktoi", "armor", 0.5, 1) + tech("X09_kataphraktoi_motor", "motorized_equipment", 0.5, 1),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("X09_the_strategikon", 7, 4, "GFX_goal_generic_army_doctrines", "A New Strategikon",
      "Strategos Leon Kekaumenos writes a modern Strategikon, as Emperor Maurice did thirteen centuries ago.",
      pre=[["X09_greek_fire"], ["X09_the_kataphraktoi"]], effect="army_experience = 10\n" + tech("X09_the_strategikon", "land_doctrine", 0.5, 1),
      filters=["FOCUS_FILTER_RESEARCH", "FOCUS_FILTER_ARMY_XP"])
focus("X09_an_army_of_new_rome", 7, 5, "GFX_goal_generic_position_armies", "An Army of New Rome",
      "Varangians, akritai, tagmata and theme levies: one army, worthy of the name of Rome.",
      pre=[["X09_the_strategikon"]], effect="add_ideas = X09_army_of_new_rome\n", filters=["FOCUS_FILTER_ARMY_XP"])


# =====================================================================================
# EXPANSION II (Oct 2026): triumphs, turncoats, the court of Sinop, the church, and more
# =====================================================================================
EXTRA_EV = ""
EXTRA_LOC = []
def event(eid, title, desc, options, picture="GFX_report_event_soldiers_marching", trigger=None):
    """Simple triggered-only country event. options = [(key_suffix, text, effect, ai_base)]"""
    global EXTRA_EV
    n = eid.split(".")[1]
    s = f"country_event = {{\n\tid = {eid}\n\ttitle = {eid}.t\n\tdesc = {eid}.d\n\tpicture = {picture}\n\tis_triggered_only = yes\n"
    if trigger: s += f"\ttrigger = {{ {trigger} }}\n"
    for suf, text, eff, ai in options:
        s += f"\n\toption = {{\n\t\tname = {eid}.{suf}\n"
        if ai is not None: s += f"\t\tai_chance = {{ base = {ai} }}\n"
        s += indent_e(eff, 2) + "\t}\n"
        EXTRA_LOC.append(f' {eid}.{suf}:0 "{q2(text)}"')
    s += "}\n\n"
    EXTRA_EV += s
    EXTRA_LOC.extend([f' {eid}.t:0 "{q2(title)}"', f' {eid}.d:0 "{q2(desc)}"'])
def indent_e(text, n):
    pad = "\t" * n
    return "".join(pad + l + "\n" for l in text.strip("\n").split("\n") if l.strip())
def q2(t): return t.replace('"', '\\"').replace("\n", "\\n")

# ---------------- the turncoat tradition: changing sides, again ----------------
focus("X09_catalan_mercenaries", 17, 3, "GFX_goal_generic_allies_build_infantry", "The Catalan Company",
      "Six hundred years ago Catalan mercenaries were hired to defend the empire and ended up sacking it. Aragon now offers us their descendants again, at a reasonable rate. The Logothete has checked the contract twice.",
      pre=[["X09_aragons_shield"]], avail="country_exists = SPC\nNOT = { has_war_with = SPC }",
      effect=("add_equipment_to_stockpile = { type = infantry_equipment amount = 1500 producer = SPC }\n"
              "add_equipment_to_stockpile = { type = artillery_equipment amount = 36 producer = SPC }\narmy_experience = 10\n"),
      filters=["FOCUS_FILTER_MANPOWER", "FOCUS_FILTER_ARMY_XP"])
focus("X09_stab_the_lion", 17, 4, "GFX_goal_generic_major_war", "The Gabras Gambit: West",
      "Theodoros Gabras founded this empire by turning on his master in the middle of a war. Aragon has armed us, trained us and turned its back to deal with the Greeks. It would be disrespectful to the founder not to.",
      pre=[["X09_catalan_mercenaries"]], avail="country_exists = SPC\nNOT = { has_war_with = SPC }",
      effect=("diplomatic_relation = { country = SPC relation = non_aggression_pact active = no }\n"
              "add_opinion_modifier = { target = SPC modifier = negative_50 }\n" + claims(52, 53, 54) +
              "create_wargoal = { type = take_state_focus target = SPC generator = { 52 53 } }\n"
              "SPC = { country_event = { id = byzantium.3 hours = 12 } }\n"),
      ai=5, filters=["FOCUS_FILTER_ANNEXATION"])
focus("X09_stab_the_khan", 19, 4, "GFX_goal_generic_major_war", "The Gabras Gambit: East",
      "The Khan's rifles are in our arsenals and the Khan's armies are spread thin from Tabriz to Basra. Three centuries ago a Byzantine general stabbed an Ilkhan in the back. It is, in a sense, a family tradition.",
      pre=[["X09_the_khans_favour"]], avail="country_exists = X63\nNOT = { has_war_with = X63 }",
      effect=("diplomatic_relation = { country = X63 relation = non_aggression_pact active = no }\n"
              "add_opinion_modifier = { target = X63 modifier = negative_50 }\n" + claims(767, 768, 771, 772, 781) +
              "create_wargoal = { type = take_state_focus target = X63 generator = { 768 771 772 } }\n"
              "X63 = { country_event = { id = byzantium.8 hours = 12 } }\n"),
      ai=3, filters=["FOCUS_FILTER_ANNEXATION"])
event("byzantium.3", "The Byzantines Have Switched Sides",
      "This morning the Byzantine envoy in Saragossa presented a declaration of war, with the same courteous smile he wore last week while thanking the King for a shipment of rifles. Our ambassador in Sinop reports that the court there considers the whole affair to be in excellent taste.",
      [("a", "Of course they have.", "add_war_support = 0.05\n", None)], picture="GFX_report_event_journalists_speech")
event("byzantium.8", "The Romans Betray the Khan",
      "Every Ilkhan is taught the story of Theodoros Gabras, the general who turned on his master in the middle of a war. Today his descendant has done it again, with our own rifles in the hands of his soldiers.",
      [("a", "We should have read our own history books.", "add_war_support = 0.05\n", None)], picture="GFX_report_event_journalists_speech")

# ---------------- the triumph: retaking Roman provinces ----------------
focus("X09_revive_the_triumph", 31, 1, "GFX_goal_generic_occupy_states_ongoing_war", "Revive the Triumph",
      "The last Roman triumph was held before the crusaders came. The Master of Ceremonies has found the old protocols in a crate in the Sinop archives: the route, the hymns, the order of the captured standards, and the precise number of times the emperor should tread on the neck of a defeated enemy (once, lightly).",
      pre=[["X09_the_throne_of_sinop"]], effect="add_ideas = X09_triumphal_tradition\n", ai=20, filters=["FOCUS_FILTER_WAR_SUPPORT"])
focus("X09_trajans_ghost", 37, 2, "GFX_goal_generic_more_territorial_claims", "Trajan's Ghost",
      "Emperor Trajan marched to the Persian Gulf and wept that he was too old to follow Alexander to India. His statue in our war ministry is said to look east. The General Staff has begun drawing maps of Mesopotamia, purely as an exercise.",
      pre=[["X09_revive_the_triumph"]], avail="country_exists = X63\nNOT = { has_war_with = X63 }\nowns_state = 772",
      effect=claims(773, 774) + "create_wargoal = { type = take_state_focus target = X63 generator = { 773 774 } }\n",
      filters=["FOCUS_FILTER_ANNEXATION"])

TRIUMPHS = [
    # id, x, y, name, desc, states, extra effect, event title, event text, pre
    ("X09_triumph_over_the_cumans", 27, 3, "Triumph over the Cumans",
     "The descendants of the horsemen who burned Constantinople parade in chains through the Golden Gate, or at least through the main street of Sinop. The Cuman horsetail standards will hang in the Holy Wisdom.",
     [754, 755], "army_experience = 25\n", "Triumph over the Cumans",
     "Six hundred years after the burning of the City, the horsetail standards of Bithynia are carried behind the emperor's chariot. Old women in the crowd spit on them. Small boys run alongside, trying to touch the captured guns. The Patriarch, who has a long memory, refuses to smile."),
    ("X09_triumph_of_ionia", 29, 3, "Triumph of Ionia",
     "Smyrna and Bursa, the cities of the old Asian themes, are Roman again. The merchants of Ionia are invited to the triumph and, more importantly, to the tax office.",
     [53, 54], build(54, "industrial_complex", 1, 1), "Triumph of Ionia",
     "Fig-sellers from Smyrna and silk-weavers from Bursa march in the triumph behind the captured Aragonese field guns. The crowd throws figs. The figs are, the Logothete notes, now subject to imperial excise."),
    ("X09_triumph_of_thrace", 31, 3, "Triumph of Thrace",
     "Adrianople, where emperors once wintered their armies, guards the western road to the City. With Thrace in Roman hands, Constantinople has a hinterland again instead of a front line.",
     [52, 753], "add_stability = 0.05\n", "Triumph of Thrace",
     "The emperor rides out through the Charisius Gate and back in through the Golden Gate, which is not strictly the traditional route, but the protocol officer has been overruled. Thracian peasants line the road with bread and salt."),
    ("X09_triumph_of_the_pontus", 33, 3, "Triumph of the Pontus",
     "Trebizond and the Armenian highlands, where the Grand Komnenoi held out for two centuries after the old empire fell, are home again.",
     [768, 781], "add_manpower = 20000\n", "Triumph of the Pontus",
     "The Pontic regiments march in the triumph in their sheepskin hats, dancing the serra with rifles in hand. The Armenian bishops who walk behind them carry relics that have not seen a Roman procession in five hundred years."),
    ("X09_triumph_of_cyprus", 35, 3, "Triumph of Cyprus",
     "Cyprus was Roman for a thousand years before it was anyone else's. The island's monasteries ring their bells for three days straight.",
     [767], "navy_experience = 25\n", "Triumph of Cyprus",
     "The Megas Doux brings the triumph ashore at the harbour, sailors first, marines second, and a captured Ilkhanid gunboat towed behind. The Cypriot delegation brings wine. The procession is noticeably slower in its second half."),
    ("X09_triumph_of_syria", 30, 4, "Triumph of Syria",
     "Antioch had been Roman for centuries, but alone. Now Aleppo and the Syrian coast stand with it, and the Patriarch of Antioch has a flock again.",
     [771, 772], "add_political_power = 100\n", "Triumph of Syria",
     "Camels in a Roman triumph. The Master of Ceremonies had warned against it. The camels, unaware of protocol, eat the laurel wreaths off the triumphal arch, and the crowd agrees it is the best triumph in living memory."),
    ("X09_triumph_of_hellas", 32, 4, "Triumph of Hellas",
     "Thessalonica, the second city of the empire, and Athens, the city of the philosophers, both answer to the Basileus. Not every Hellene is happy about it.",
     [70, 49], "add_manpower = 15000\n", "Triumph of Hellas",
     "The emperor enters Thessalonica by the Arch of Galerius, as emperors did sixteen hundred years ago. The welcome is warm in the churches and cool in the cafes, where a good many Hellenes still consider themselves Hellenes. The censors have been told to be patient."),
    ("X09_triumph_of_mesopotamia", 37, 3, "Trajan's Triumph",
     "Mosul and Baghdad, the furthest marches of Trajan's war, are under the Roman eagle. The generals have stopped pretending it was an exercise.",
     [773, 774], "if = { limit = { owns_state = 774 } add_resource = { type = oil amount = 8 state = 774 } }\n", "Trajan's Triumph",
     "No Roman emperor has ever held a triumph for Mesopotamia and kept it. The emperor, who has read his history, orders the triumph held in Baghdad instead of the City, on the reasonable grounds that he may not get another chance."),
]
for i, (fid, x, y, name, desc, states, extra, et, ed) in enumerate(TRIUMPHS, 11):
    pre = [["X09_trajans_ghost"]] if fid == "X09_triumph_of_mesopotamia" else [["X09_revive_the_triumph"]]
    focus(fid, x, y, "GFX_goal_generic_occupy_states_ongoing_war", name, desc, pre=pre,
          avail="".join(f"owns_state = {s}\n" for s in states),
          effect=("".join(f"add_state_core = {s}\n" for s in states) + "add_stability = 0.05\nadd_war_support = 0.05\nadd_political_power = 50\n"
                  + extra + f"country_event = {{ id = byzantium.{i} days = 1 }}\n"),
          ai=10, filters=["FOCUS_FILTER_STABILITY", "FOCUS_FILTER_WAR_SUPPORT"])
    event(f"byzantium.{i}", et, ed, [("a", "Polla ta eti!", "add_stability = 0.02\n", None)], picture="GFX_report_event_soldiers_marching")
TRIUMPH_IDS = [t[0] for t in TRIUMPHS]

focus("X09_the_restored_oikoumene", 31, 6, "GFX_goal_generic_national_unity", "The Restored Oikoumene",
      "From the Danube to the Euphrates, Romans live under Roman law again. The Oikoumene, the inhabited world, is not quite whole, but the emperor's cartographers have been told to draw it as if it were.",
      pre=[["X09_revive_the_triumph"]],
      avail="calc_true_if = { amount = 4 " + " ".join(f"has_completed_focus = {t}" for t in TRIUMPH_IDS) + " }",
      effect="remove_ideas = X09_triumphal_tradition\nadd_ideas = X09_restored_oikoumene\n", ai=30, filters=["FOCUS_FILTER_STABILITY"])
focus("X09_the_pentarchy", 30, 7, "GFX_focus_generic_treaty", "The Pentarchy",
      "Constantinople, Antioch, Alexandria, Jerusalem and Rome: the five ancient patriarchates. The emperor invites four of the five patriarchs to a council in the Holy Wisdom. The fifth, in Rome, is not answering his letters.",
      pre=[["X09_the_restored_oikoumene"]],
      effect="add_stability = 0.1\nadd_political_power = 100\nif = { limit = { country_exists = X27 } add_opinion_modifier = { target = X27 modifier = positive_50 } }\n",
      filters=["FOCUS_FILTER_STABILITY"])
focus("X09_pax_romana", 32, 7, "GFX_goal_generic_national_unity", "Pax Romana",
      "Roman roads, Roman courts, Roman coins and Roman garrisons from Thrace to Syria. The empire's subjects grumble about the taxes, as Roman subjects always have, and travel safely, as they have not for centuries.",
      pre=[["X09_the_restored_oikoumene"]], effect="add_ideas = X09_pax_romana\n", filters=["FOCUS_FILTER_INDUSTRY", "FOCUS_FILTER_STABILITY"])
focus("X09_the_thousand_year_empire", 31, 8, "GFX_focus_hun_elect_a_king", "The Thousand-Year Empire",
      "Rome fell, rose in the east, fell to the crusaders, was burned by the Cumans, rose again from a rebel's camp in Sinop and has now come home. The empire is older than every state that tried to end it. It intends to outlive the rest.",
      pre=[["X09_the_pentarchy"], ["X09_pax_romana"]], avail="owns_state = 52",
      effect="add_stability = 0.15\nadd_war_support = 0.1\narmy_experience = 50\nnavy_experience = 25\nadd_political_power = 150\n",
      filters=["FOCUS_FILTER_STABILITY", "FOCUS_FILTER_ARMY_XP"])

# ---------------- the church ----------------
focus("X09_council_of_sinop", 9, 3, "GFX_focus_generic_treaty", "The Council of Sinop",
      "The bishops of Anatolia, Antioch and the Pontus gather in Sinop for the first council in a century. The agenda: the calendar, the liturgy, and whether the Patriarch may legally be enthroned in a city he cannot enter. They agree on the third.",
      pre=[["X09_the_patriarch_in_exile"]], effect="add_political_power = 75\nadd_stability = 0.03\n", filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_the_hesychasts", 9, 4, "GFX_goal_generic_national_unity", "The Hesychasts of Cappadocia",
      "In the cave monasteries of Göreme, hermits still practise the prayer of silence. Pilgrims walk for weeks to sit with them. The empire would do well to be seen walking with the pilgrims.",
      pre=[["X09_council_of_sinop"]], effect="add_ideas = X09_hesychast_revival\n", filters=["FOCUS_FILTER_STABILITY"])
focus("X09_the_hodegetria", 9, 5, "GFX_goal_generic_propaganda", "Parade the Hodegetria",
      "The icon of the Hodegetria, painted (the monks insist) by Saint Luke himself, was smuggled out of the burning City by a Cuman's Greek concubine. It has not left its chapel since. It will now tour every garrison in the empire.",
      pre=[["X09_the_hesychasts"]], effect="add_war_support = 0.1\n", filters=["FOCUS_FILTER_WAR_SUPPORT"])
focus("X09_the_monks_of_sumela", 9, 6, "GFX_goal_generic_construct_infrastructure", "The Monks of Sumela",
      "The cliffside monastery of Sumela above Trebizond is empty, its frescoes scratched by Ilkhanid soldiers. Monks from Athos and Cappadocia volunteer to bring it back to life.",
      pre=[["X09_the_hodegetria"]], avail="owns_state = 768",
      effect="add_stability = 0.05\n" + build(768, "infrastructure", 1), filters=["FOCUS_FILTER_STABILITY"])

# ---------------- the court of Sinop ----------------
focus("X09_the_book_of_ceremonies", 12, 6, "GFX_goal_generic_political_pressure", "The Book of Ceremonies",
      "Constantine VII wrote down how every imperial ceremony should be done: who bows, who kneels, who may wear which shade of purple. The court of Sinop has been improvising for three hundred years. No longer.",
      pre=[["X09_the_basileia_endures"]], effect="add_political_power = 100\n", filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_the_secret_office", 10, 7, "GFX_goal_generic_propaganda", "The Office of the Barbarians",
      "The old Skrinion ton Barbaron kept files on every foreign prince, his debts, his mistresses and his favourite horse. Theophano Doukaina, who has been keeping such files privately for years, is invited to make it official.",
      pre=[["X09_the_book_of_ceremonies"]],
      effect="if = { limit = { has_dlc = \"La Resistance\" } create_intelligence_agency = yes }\nadd_political_power = 50\n",
      filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_the_hippodrome", 12, 7, "GFX_goal_generic_national_unity", "The Hippodrome of Sinop",
      "Chariot racing never died in the empire. The Blues and the Greens still race every Sunday, still brawl every Monday and still decide more elections to the city council than the city council does.",
      pre=[["X09_the_book_of_ceremonies"]], effect="add_stability = 0.05\n", filters=["FOCUS_FILTER_STABILITY"])
focus("X09_patronise_the_blues", 11, 8, "GFX_goal_generic_political_pressure", "Patronise the Blues",
      "The Blues are the faction of the old families, the bureaucracy and the officers' mess. The emperor appears in the imperial box in a blue cloak.",
      pre=[["X09_the_hippodrome"]], excl=["X09_patronise_the_greens"],
      effect="add_ideas = X09_the_blues\ncountry_event = { id = byzantium.4 days = 30 }\n", ai=2, filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_patronise_the_greens", 13, 8, "GFX_goal_generic_trade", "Patronise the Greens",
      "The Greens are the faction of the harbour, the guilds and the merchant houses. The emperor appears in the imperial box in a green cloak, and the price of green dye triples overnight.",
      pre=[["X09_the_hippodrome"]], excl=["X09_patronise_the_blues"],
      effect="add_ideas = X09_the_greens\ncountry_event = { id = byzantium.4 days = 30 }\n", ai=2, filters=["FOCUS_FILTER_INDUSTRY"])
event("byzantium.4", "Riot in the Hippodrome",
      "After a disputed finish in the Sunday race, the losing faction tore up the benches, set fire to the stables and marched on the palace chanting \"Nika!\", the old cry of the riot that nearly toppled Justinian. The Varangians are waiting for orders.",
      [("a", "Send in the Varangians.", "add_stability = -0.05\nadd_war_support = 0.05\nset_country_flag = X09_nika_crushed\n", 50),
       ("b", "Pay for new stables. And new benches. And free bread.", "add_political_power = -75\nadd_stability = 0.03\n", 50)],
      picture="GFX_report_event_generic_riot")
focus("X09_never_another_nika", 12, 9, "GFX_goal_generic_national_unity", "Never Another Nika",
      "The racing will go on, and the factions will go on shouting at each other, but from now on they do it with the emperor's permission and within the emperor's walls.",
      pre=[["X09_patronise_the_blues", "X09_patronise_the_greens"]], effect="add_stability = 0.1\n", filters=["FOCUS_FILTER_STABILITY"])
focus("X09_purple_ink", 14, 7, "GFX_goal_generic_political_pressure", "Purple Ink",
      "Only the emperor may sign in purple ink. Every decree, every appointment, every tax: one signature, in one colour, from one desk.",
      pre=[["X09_the_book_of_ceremonies"]], effect="add_ideas = X09_purple_ink\n", filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_a_bride_for_the_basileus", 15, 8, "GFX_focus_generic_treaty", "A Bride for the Basileus",
      "The imperial bride-show is held in the old way: the most suitable daughters of the empire and its friends are invited to Sinop, and the emperor offers a golden apple to his choice. This year a Scandinavian princess and a Greek admiral's daughter are the favourites.",
      pre=[["X09_purple_ink"]],
      effect=("add_stability = 0.05\n"
              "if = { limit = { country_exists = SCA } add_opinion_modifier = { target = SCA modifier = positive_50 } SCA = { add_opinion_modifier = { target = ROOT modifier = positive_50 } } }\n"
              "if = { limit = { country_exists = GRE } add_opinion_modifier = { target = GRE modifier = positive_50 } GRE = { add_opinion_modifier = { target = ROOT modifier = positive_50 } } }\n"),
      filters=["FOCUS_FILTER_POLITICAL"])
focus("X09_the_old_emperors_audience", 14, 2, "GFX_focus_hun_elect_a_king", "The Old Emperor's Last Audience",
      "Tiberios V receives the court one last time, seated on the throne of Theodoros Gabras with the mechanical golden lions at his feet. The lions roar when he raises his hand. One of them squeaks.",
      pre=[["X09_legacy_of_gabras"]], effect="add_political_power = 50\ncountry_event = { id = byzantium.6 days = 3 }\n",
      filters=["FOCUS_FILTER_POLITICAL"])
event("byzantium.6", "The Old Emperor Speaks",
      "Tiberios V spoke for nearly an hour, which his physicians had forbidden. He reminded the court that Gabras had changed sides four times in his life and died in bed as emperor, that every enemy of Rome had eventually become a footnote, and that the mechanical lions needed oiling. Then he blessed his son, the Domestikos and the senators in turn, and asked to be carried back to his rooms.",
      [("a", "Long live the Emperor.", "add_stability = 0.05\n", None)], picture="GFX_report_event_journalists_speech")

# ---------------- army additions ----------------
focus("X09_call_the_northmen", 5, 3, "GFX_goal_generic_allies_build_infantry", "Letters to the North",
      "Harald Eiriksson writes home to the fjords: the pay is good, the wine is better and the emperor needs men. The Scandinavian papers print his letter on the front page.",
      pre=[["X09_the_varangian_guard"]], effect="country_event = { id = byzantium.5 days = 14 }\n", filters=["FOCUS_FILTER_MANPOWER"])
event("byzantium.5", "Volunteers from the North",
      "Several hundred Scandinavian volunteers have arrived in Sinop, most of them farm boys who have read too many sagas, a few of them veterans of the northern wars, and one of them a ninety-year-old who claims his grandfather served in the Guard. They ask to swear the Varangian oath.",
      [("a", "Give them axes for the ceremony and rifles for the front.", "add_manpower = 6000\narmy_experience = 10\n", 70),
       ("b", "Put the old man in charge of the regimental museum.", "add_political_power = 50\nadd_manpower = 3000\n", 30)],
      picture="GFX_report_event_soldiers_marching")
focus("X09_songs_of_digenis_akritas", 8, 4, "GFX_goal_generic_propaganda", "Songs of Digenis Akritas",
      "Every child on the eastern frontier knows the ballads of Digenis Akritas, half-Roman and half-Arab, who wrestled Death himself on a marble threshing floor. The war ministry commissions new verses, with rifles.",
      pre=[["X09_the_kataphraktoi"]], effect="add_war_support = 0.05\narmy_experience = 10\n", filters=["FOCUS_FILTER_WAR_SUPPORT"])
focus("X09_the_athanatoi", 6, 6, "GFX_goal_generic_special_forces", "The Athanatoi",
      "The Immortals were the emperor's elite regiment, revived by John Tzimiskes. They will be revived once more, with the best men of every theme.",
      pre=[["X09_an_army_of_new_rome"]], effect="load_oob = \"X09_athanatoi\"\n" + tech("X09_the_athanatoi", "special_forces", 0.5, 1),
      filters=["FOCUS_FILTER_MANPOWER", "FOCUS_FILTER_RESEARCH"])
focus("X09_wings_of_saint_michael", 8, 6, "GFX_goal_generic_build_airforce", "The Wings of Saint Michael",
      "The Archangel Michael, commander of the heavenly host, is the obvious patron of an air force. The first squadron is blessed on the parade ground at Ankara and crashes only once.",
      pre=[["X09_an_army_of_new_rome"]], effect="air_experience = 25\n" + build(63, "air_base", 2) + tech("X09_wings_of_saint_michael", "light_fighter", 0.5, 1),
      filters=["FOCUS_FILTER_AIR_XP", "FOCUS_FILTER_RESEARCH"])
focus("X09_the_scholai", 6, 7, "GFX_goal_generic_army_doctrines", "The Scholai",
      "The Scholai were the oldest guard regiments of the empire. Their name now belongs to the staff college in Ankara, run by the formidable Ioannis Kourkouas.",
      pre=[["X09_the_athanatoi"]], effect="army_experience = 15\n", filters=["FOCUS_FILTER_ARMY_XP"])
focus("X09_the_optimatoi", 8, 7, "GFX_goal_generic_cavalry", "The Optimatoi",
      "Mountain troops for the Taurus and the Pontic Alps, under Leontios Skleros, who has never lost a fight he started on high ground.",
      pre=[["X09_an_army_of_new_rome"]], effect="recruit_character = X09_leontios_skleros\n" + tech("X09_the_optimatoi", "mountaineers_tech", 0.5, 1),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("X09_the_siphon_corps", 7, 8, "GFX_goal_generic_army_artillery2", "The Siphon Corps",
      "Greek fire was sprayed from bronze siphons on the prows of dromons. Its descendant is the flamethrower, and the engineers of the Siphon Corps are very keen on it.",
      pre=[["X09_the_scholai", "X09_the_optimatoi"]], effect=tech("X09_the_siphon_corps", "support_tech", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("X09_mobilise_the_themata", 7, 9, "GFX_goal_generic_allies_build_infantry", "Mobilise the Themata",
      "Every theme raises its levy, every village sends its sons. The Roman army has never been large, but it has always been everywhere.",
      pre=[["X09_the_siphon_corps"]], effect="add_manpower = 30000\nadd_war_support = 0.05\n", filters=["FOCUS_FILTER_MANPOWER"])

# ---------------- navy additions ----------------
focus("X09_the_dromon_program", 0, 6, "GFX_goal_generic_navy_cruiser", "The Dromon Programme",
      "The dromon was the warship of the old empire: fast, oared and armed with Greek fire. Its successor will be a fast destroyer, and the admirals insist on calling it a dromon.",
      pre=[["X09_masters_of_the_bosporus"]], effect="navy_experience = 15\n" + tech("X09_the_dromon_program", "dd_tech", 0.5, 2),
      filters=["FOCUS_FILTER_NAVY_XP", "FOCUS_FILTER_RESEARCH"])
focus("X09_golden_horn_arsenal", 0, 7, "GFX_goal_generic_construct_naval_dockyard", "The Arsenal of the Golden Horn",
      "The great naval arsenal of the Golden Horn built the fleets that held the Mediterranean for five centuries. Its slipways are buried under Cuman ash. They will be dug out.",
      pre=[["X09_the_dromon_program"]], avail="owns_state = 52", effect=build(52, "dockyard", 2, 2), filters=["FOCUS_FILTER_INDUSTRY"])

# ---------------- economy additions ----------------
focus("X09_the_silk_monopoly", 4, 5, "GFX_goal_generic_trade", "The Imperial Silk Monopoly",
      "Justinian smuggled silkworms out of China in the hollow staffs of two monks. Their descendants still spin in Antioch, and the state still owns every one of them.",
      pre=[["X09_the_silk_road_of_antioch"]], effect="add_ideas = X09_silk_monopoly\n", filters=["FOCUS_FILTER_INDUSTRY"])
focus("X09_the_hazelnut_fleet", 4, 6, "GFX_goal_generic_trade", "The Hazelnut Fleet",
      "Sinop and the Pontic coast grow most of the world's hazelnuts. A state shipping company will carry them, and bring back what the empire cannot make.",
      pre=[["X09_the_silk_monopoly"]], effect="add_equipment_to_stockpile = { type = convoy_1 amount = 30 producer = X09 }\nadd_political_power = 50\n",
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("X09_electrify_anatolia", 2, 7, "GFX_goal_generic_construct_civ_factory", "Electrify Anatolia",
      "Hydroelectric dams on the Halys and the Sakarya, power lines to Ankara and Konya, and electric light in villages that still read by oil lamps.",
      pre=[["X09_the_golden_bezant"]], effect=build(95, "industrial_complex", 1, 1) + build(56, "industrial_complex", 1, 1),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("X09_the_kastamonu_refinery", 1, 8, "GFX_goal_generic_oil_refinery", "The Kastamonu Refinery",
      "The empire has no oil. It has coal and engineers. That will have to do.",
      pre=[["X09_electrify_anatolia"]], effect=build(56, "synthetic_refinery", 1, 1), filters=["FOCUS_FILTER_INDUSTRY"])
focus("X09_black_sea_grain", 3, 8, "GFX_goal_generic_production", "Black Sea Grain",
      "Grain from the Pontic steppe and Cappadocia fed Constantinople for a thousand years. With full granaries, the empire can afford to mobilise.",
      pre=[["X09_electrify_anatolia"]], effect="add_stability = 0.05\nadd_manpower = 5000\n", filters=["FOCUS_FILTER_STABILITY", "FOCUS_FILTER_MANPOWER"])
focus("X09_an_imperial_economy", 2, 9, "GFX_goal_generic_construct_mil_factory", "An Economy Fit for an Empire",
      "Factories in Ankara, shipyards in Sinop, refineries in Kastamonu and silk in Antioch. The Basileia can finally afford its own ambitions.",
      pre=[["X09_the_kastamonu_refinery"], ["X09_black_sea_grain"]],
      effect="add_ideas = X09_imperial_economy\n" + build(63, "arms_factory", 1, 1), filters=["FOCUS_FILTER_INDUSTRY"])

# ---------------- Constantinople additions ----------------
focus("X09_the_road_to_adrianople", 22, 8, "GFX_goal_generic_territory_or_war", "The Road to Adrianople",
      "Constantinople without Thrace is a besieged city. Adrianople must be Roman too.",
      pre=[["X09_enter_the_golden_gate"]], avail="country_exists = SPC\n753 = { is_owned_by = SPC }\nNOT = { has_war_with = SPC }",
      effect=claims(753) + "create_wargoal = { type = take_state_focus target = SPC generator = { 753 } }\n",
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("X09_the_founders_bones", 16, 8, "GFX_goal_generic_national_unity", "The Founder Comes Home",
      "Theodoros Gabras asked to be buried in Constantinople, a city he never saw. Three hundred years late, his coffin crosses the Bosporus on a purple-draped barge.",
      pre=[["X09_enter_the_golden_gate"]], effect="add_stability = 0.05\nadd_war_support = 0.05\ncountry_event = { id = byzantium.7 days = 2 }\n",
      filters=["FOCUS_FILTER_STABILITY"])
event("byzantium.7", "The Founder Comes Home",
      "The procession carrying the remains of Theodoros Gabras stopped at every church between the Bosporus and the Holy Apostles. At the last of them, an elderly Ilkhanid diplomat stepped out of the crowd, bowed to the coffin and said, quite audibly, \"He still owes us an army.\" The crowd laughed. The emperor did not.",
      [("a", "Bury him with the emperors.", "add_stability = 0.03\n", None)], picture="GFX_report_event_journalists_speech")
focus("X09_the_synoikismos", 17, 10, "GFX_goal_generic_construct_infrastructure", "The Synoikismos",
      "Constantine populated his new city by ordering senators to move there. His successor will do the same with tax exemptions, free land and a great deal of shouting.",
      pre=[["X09_the_theodosian_walls"]], effect=build(52, "infrastructure", 1) + "add_victory_points = { province = 9833 value = 10 }\nadd_manpower = 10000\n",
      filters=["FOCUS_FILTER_MANPOWER"])
focus("X09_the_magnaura", 21, 10, "GFX_focus_research", "The University of the Magnaura",
      "The Magnaura was the first university in Europe. Its reopening is attended by every scholar in the empire, both of them.",
      pre=[["X09_hagia_sophia"]], effect="add_ideas = X09_magnaura\n", filters=["FOCUS_FILTER_RESEARCH"])
focus("X09_the_milion", 19, 11, "GFX_goal_generic_construct_infrastructure", "The Milion",
      "Every distance in the empire was once measured from a single marble milestone near the Holy Wisdom. It is rebuilt, and the empire's roads are measured from it again.",
      pre=[["X09_emperor_of_the_romans"]],
      effect="every_owned_state = { limit = { is_core_of = ROOT } add_building_construction = { type = infrastructure level = 1 instant_build = yes } }\n",
      filters=["FOCUS_FILTER_INDUSTRY"])

# ---------------- the Greek question, continued ----------------
focus("X09_joint_aegean_patrols", 23, 5, "GFX_goal_generic_navy_doctrines_tactics", "Joint Aegean Patrols",
      "Byzantine and Greek gunboats hunt Aragonese smugglers together between the islands. The crews communicate in the same language, and argue in it constantly.",
      pre=[["X09_the_orthodox_league"]], effect="navy_experience = 15\n" + tech("X09_joint_aegean_patrols", "naval_doctrine", 0.5, 1),
      filters=["FOCUS_FILTER_NAVY_XP"])
focus("X09_an_orthodox_commonwealth", 23, 6, "GFX_focus_generic_treaty", "An Orthodox Commonwealth",
      "Romans and Hellenes are two states, one Church and, if the diplomats have their way, one customs union.",
      pre=[["X09_joint_aegean_patrols"]], effect="add_stability = 0.05\nadd_ideas = X09_orthodox_commonwealth\n", filters=["FOCUS_FILTER_STABILITY"])
focus("X09_the_despotate_of_the_morea", 25, 5, "GFX_goal_generic_national_unity", "The Despotate of the Morea",
      "In the last century of the old empire, the Peloponnese was ruled from Mystras by the emperor's brothers. The office of Despot is revived, and the Moreots get a Roman prince of their own.",
      pre=[["X09_bring_the_hellenes_home"]], avail="owns_state = 62",
      effect="add_state_core = 62\nadd_stability = 0.05\n", filters=["FOCUS_FILTER_STABILITY"])
focus("X09_thessalonica_second_city", 25, 6, "GFX_goal_generic_construct_civ_factory", "Thessalonica, Second City",
      "Thessalonica was the second city of the empire for a thousand years. It will be again.",
      pre=[["X09_the_despotate_of_the_morea"]], avail="owns_state = 70",
      effect="add_state_core = 70\n" + build(70, "industrial_complex", 1, 1), filters=["FOCUS_FILTER_INDUSTRY"])

EXTRA_IDEAS = [
    ("X09_triumphal_tradition", "warrior_traditions_idea", "war_support_factor = 0.05\nexperience_gain_army_factor = 0.05",
     "The Triumphal Tradition", "Every reconquered province earns a procession, a holiday and a new mosaic."),
    ("X09_restored_oikoumene", "generic_national_unification", "stability_factor = 0.1\nwar_support_factor = 0.05\nresistance_target = -0.15\ncompliance_growth = 0.05",
     "The Restored Oikoumene", "Romans live under Roman law from Thrace to the Euphrates."),
    ("X09_pax_romana", "generic_production_bonus", "industrial_capacity_factory = 0.1\nconsumer_goods_factor = -0.05\nproduction_speed_buildings_factor = 0.1",
     "Pax Romana", "Roman roads, Roman courts and Roman coins."),
    ("X09_hesychast_revival", "generic_pp_unity_bonus", "stability_factor = 0.05\ndrift_defence_factor = 0.1",
     "Hesychast Revival", "Pilgrims crowd the cave monasteries of Cappadocia."),
    ("X09_the_blues", "generic_pp_unity_bonus", "political_power_gain = 0.1\narmy_org_factor = 0.03",
     "Patron of the Blues", "The emperor sits with the old families and the officers' mess."),
    ("X09_the_greens", "generic_production_bonus", "consumer_goods_factor = -0.03\nproduction_speed_buildings_factor = 0.05",
     "Patron of the Greens", "The emperor sits with the harbour, the guilds and the merchant houses."),
    ("X09_purple_ink", "generic_pp_unity_bonus", "political_power_gain = 0.1",
     "Purple Ink", "One signature, in one colour, from one desk."),
    ("X09_silk_monopoly", "generic_production_bonus", "political_power_gain = 0.05\nconsumer_goods_factor = -0.02",
     "The Imperial Silk Monopoly", "Every silkworm in Antioch belongs to the emperor."),
    ("X09_imperial_economy", "generic_production_bonus", "industrial_capacity_factory = 0.05\nindustrial_capacity_dockyard = 0.05",
     "An Economy Fit for an Empire", "The Basileia can afford its ambitions."),
    ("X09_magnaura", "generic_research_bonus", "research_speed_factor = 0.05",
     "The University of the Magnaura", "Scholars from across the Orthodox world study in Constantinople."),
    ("X09_orthodox_commonwealth", "generic_pp_unity_bonus", "stability_factor = 0.05\nopinion_gain_monthly_factor = 0.1",
     "An Orthodox Commonwealth", "Two states, one Church."),
]

# ================= emit focus tree =================
def indent(text, n):
    pad = "\t" * n
    return "".join(pad + l + "\n" if l.strip() else "\n" for l in text.strip("\n").split("\n"))
out = ["focus_tree = {\n\tid = X09_focus\n\n\tcountry = {\n\t\tfactor = 0\n\t\tmodifier = {\n\t\t\tadd = 10\n\t\t\toriginal_tag = X09\n\t\t}\n\t}\n\n\tdefault = no\n\n\tinitial_show_position = { focus = X09_the_throne_of_sinop }\n\n"]
for f in F:
    s = "\tfocus = {\n" + f"\t\tid = {f['id']}\n\t\ticon = {f['icon']}\n\t\tx = {f['x']}\n\t\ty = {f['y']}\n\t\tcost = {f['cost']}\n"
    for g in f["pre"]: s += "\t\tprerequisite = { " + " ".join(f"focus = {p}" for p in g) + " }\n"
    if f["excl"]: s += "\t\tmutually_exclusive = { " + " ".join(f"focus = {p}" for p in f["excl"]) + " }\n"
    if f["avail"]: s += "\t\tavailable = {\n" + indent(f["avail"], 3) + "\t\t}\n"
    if f["bypass"]: s += "\t\tbypass = {\n" + indent(f["bypass"], 3) + "\t\t}\n"
    if f["filters"]: s += "\t\tsearch_filters = { " + " ".join(f["filters"]) + " }\n"
    s += "\t\tcompletion_reward = {\n" + indent(f["effect"], 3) + "\t\t}\n"
    s += f"\t\tai_will_do = {{ factor = {f['ai']} }}\n\t}}\n\n"
    out.append(s)
out.append("}\n")
open(J("common/national_focus/X09_NF.txt"), "w", encoding="utf-8", newline="\n").write("".join(out))

# ================= ideas =================
IDEAS = [
    ("X09_reforming_autocrat", "generic_pp_unity_bonus", "political_power_gain = 0.15\nstability_factor = 0.05",
     "The Reforming Autocrat", "Michael VI rules alone, and rules in a hurry."),
    ("X09_rule_of_the_tagmata", "generic_infantry_bonus", "war_support_factor = 0.1\nconscription = 0.01\nexperience_gain_army_factor = 0.1\nstability_factor = -0.05",
     "Rule of the Tagmata", "The army governs the empire."),
    ("X09_senatorial_charter", "generic_democratic_drift_bonus", "stability_factor = 0.1\npolitical_power_gain = 0.05\nresearch_speed_factor = 0.03",
     "The Senatorial Charter", "The Senate of New Rome governs; the emperor reigns."),
    ("X09_roman_pride", "generic_national_unification", "stability_factor = 0.05\nwar_support_factor = 0.05\narmy_core_attack_factor = 0.05",
     "Neither Latin nor Mongol", "Byzantium is nobody's frontier but its own."),
    ("X09_reformed_themes", "generic_recruit_centers", "conscription = 0.01\nstability_factor = 0.05\nproduction_speed_buildings_factor = 0.05",
     "The Reformed Themes", "Every province is a military district, and every district has a governor who answers to Sinop."),
    ("X09_golden_bezant", "generic_production_bonus", "industrial_capacity_factory = 0.05\nconsumer_goods_factor = -0.03",
     "The Golden Bezant", "A sound currency for a serious empire."),
    ("X09_army_of_new_rome", "warrior_traditions_idea", "army_attack_factor = 0.05\narmy_org_factor = 0.05",
     "An Army of New Rome", "One army, worthy of the name of Rome."),
    ("X09_ecumenical_throne", "generic_pp_unity_bonus", "stability_factor = 0.1\npolitical_power_gain = 0.1",
     "The Ecumenical Throne", "The Patriarch is home in Constantinople."),
    ("X09_new_rome", "generic_national_unification", "stability_factor = 0.1\nwar_support_factor = 0.1\nindustrial_capacity_factory = 0.05",
     "New Rome", "The Emperor of the Romans rules from the Queen of Cities."),
]
IDEAS += EXTRA_IDEAS
s = "ideas = {\n\tcountry = {\n"
for key, pic, mod, _, _ in IDEAS:
    s += f"\t\t{key} = {{\n\t\t\tpicture = {pic}\n\t\t\tallowed = {{ always = no }}\n\t\t\tremoval_cost = -1\n\t\t\tmodifier = {{\n" + indent(mod, 4) + "\t\t\t}\n\t\t}\n"
s += "\t}\n}\n"
open(J("common/ideas/X09_focus_ideas.txt"), "w", encoding="utf-8", newline="\n").write(s)

# ================= characters =================
def portrait(gfx, kinds=("civilian",)):
    s = "\t\tportraits={\n"
    for k in kinds:
        s += f"\t\t\t{k}={{\n\t\t\t\tlarge=\"{gfx}\"\n\t\t\t\tsmall=\"{gfx}_small\"\n\t\t\t}}\n"
    return s + "\t\t}\n"
CHARS = []
def country_leader(ideology):
    return f"\t\tcountry_leader={{\n\t\t\tideology={ideology}\n\t\t\texpire=\"1975.1.1.1\"\n\t\t\tid=-1\n\t\t}}\n"
def advisor(key, slot, trait, focus_id, cost=150):
    return (f"\t\tadvisor={{\n\t\t\tslot = {slot}\n\t\t\tidea_token = {key}\n\t\t\tallowed = {{ original_tag = X09 }}\n"
            f"\t\t\tavailable = {{ has_completed_focus = {focus_id} }}\n\t\t\ttraits = {{ {trait} }}\n\t\t\tcost = {cost}\n\t\t\tai_will_do = {{ factor = 1 }}\n\t\t}}\n")
def commander(kind, traits, skill, a, d, p, l):
    return (f"\t\t{kind}={{\n\t\t\ttraits={{ {traits} }}\n\t\t\tskill={skill}\n\t\t\tattack_skill={a}\n\t\t\tdefense_skill={d}\n"
            f"\t\t\tplanning_skill={p}\n\t\t\tlogistics_skill={l}\n\t\t\tlegacy_id=0\n\t\t}}\n")
def admiral(skill, a, d, m, c):
    return (f"\t\tnavy_leader={{\n\t\t\tskill={skill}\n\t\t\tattack_skill={a}\n\t\t\tdefense_skill={d}\n"
            f"\t\t\tmaneuvering_skill={m}\n\t\t\tcoordination_skill={c}\n\t\t\tlegacy_id=0\n\t\t}}\n")

CHARS.append(("X09_michael_gabras", "Michael VI Gabras", portrait("GFX_GRE_Alexander") + country_leader("absolute_monarchy")))
CHARS.append(("X09_nikephoros_vranas", "Nikephoros Vranas", portrait("GFX_GRE_Nikolaos_Plastiras", ("civilian", "army"))
              + country_leader("dictatorship") + commander("field_marshal", "old_guard", 3, 3, 3, 2, 2)))
CHARS.append(("X09_konstantinos_laskaris", "Konstantinos Laskaris", portrait("GFX_GRE_Alexandros_Svolos") + country_leader("conservatism")))
CHARS.append(("X09_patriarch_photios", "Patriarch Photios IV", portrait("GFX_GRE_Athanasios_Klaras") + advisor("X09_patriarch_photios", "political_advisor", "popular_figurehead", "X09_the_patriarch_in_exile")))
CHARS.append(("X09_ioannis_akropolites", "Ioannis Akropolites", portrait("GFX_GRE_George_Santios") + advisor("X09_ioannis_akropolites", "political_advisor", "silent_workhorse", "X09_legacy_of_gabras")))
CHARS.append(("X09_manuel_apokaukos", "Manuel Apokaukos", portrait("GFX_GRE_Nikos_Ploumpidis") + advisor("X09_manuel_apokaukos", "political_advisor", "captain_of_industry", "X09_the_pontic_economy")))
CHARS.append(("X09_leon_kekaumenos", "Leon Kekaumenos", portrait("GFX_GRE_Alexandros_Sakellariou") + advisor("X09_leon_kekaumenos", "theorist", "military_theorist", "X09_the_strategikon")))
CHARS.append(("X09_harald_eiriksson", "Harald Eiriksson", portrait("GFX_portrait_europe_generic_land_9", ("army",)) + commander("corps_commander", "trickster", 3, 4, 2, 2, 1)))
CHARS.append(("X09_alexios_notaras", "Megas Doux Alexios Notaras", portrait("GFX_GRE_Petros_Voulgaris", ("navy",)) + admiral(2, 2, 2, 3, 2)))
CHARS.append(("X09_theophano_doukaina", "Theophano Doukaina", portrait("gfx/leaders/Europe/portrait_europe_generic_operative_female_3.dds").replace('\t\t\t\tsmall="gfx/leaders/Europe/portrait_europe_generic_operative_female_3.dds_small"\n', '') + advisor("X09_theophano_doukaina", "political_advisor", "compassionate_gentleman", "X09_the_secret_office")))
CHARS.append(("X09_ioannis_kourkouas", "Ioannis Kourkouas", portrait("GFX_GRE_Konstantinos_Maniadakis") + advisor("X09_ioannis_kourkouas", "army_chief", "army_chief_offensive_1", "X09_the_scholai")))
CHARS.append(("X09_leontios_skleros", "Leontios Skleros", portrait("GFX_GRE_Nikos_Beloyannis", ("army",)) + commander("corps_commander", "trickster", 3, 2, 3, 3, 2)))

cs = "characters={\n"
for key, _, body in CHARS:
    cs += f"\t{key}={{\n\t\tname={key}\n" + body + "\t}\n\n"
cs += "}\n"
open(J("common/characters/X09_focus_characters.txt"), "w", encoding="utf-8", newline="\n").write(cs)

# ================= events =================
EV = '''add_namespace = byzantium

# The Roman emperor enters Constantinople
news_event = {
	id = byzantium.1
	title = byzantium.1.t
	desc = byzantium.1.d
	picture = GFX_news_event_generic_sign_treaty2
	major = yes
	is_triggered_only = yes

	option = {
		name = byzantium.1.a
		trigger = { tag = X09 }
	}
	option = {
		name = byzantium.1.b
		trigger = { NOT = { tag = X09 } }
	}
}
'''
open(J("events/byzantium.txt"), "w", encoding="utf-8", newline="\n").write(EV + "\n" + EXTRA_EV)

# ================= OOB =================
oob = ("division_template = {\n\tname = \"Varangian Guard\"\n\tregiments = {\n"
       + "".join(f"\t\tinfantry = {{ x = {x} y = {y} }}\n" for x in range(3) for y in range(3))
       + "\t}\n\tsupport = {\n\t\tartillery = { x = 0 y = 0 }\n\t}\n}\n\nunits = {\n")
for name in ("1st Varangian Guard", "2nd Varangian Guard"):
    oob += f"\tdivision = {{\n\t\tname = \"{name}\"\n\t\tlocation = 6995\n\t\tdivision_template = \"Varangian Guard\"\n\t\tstart_experience_factor = 0.6\n\t\tstart_equipment_factor = 1.0\n\t}}\n"
oob += "}\n"
open(J("history/units/X09_varangian_guard.txt"), "w", encoding="utf-8", newline="\n").write(oob)
ath = ("division_template = {\n\tname = \"Athanatoi\"\n\tregiments = {\n"
       + "".join(f"\t\tinfantry = {{ x = {x} y = {y} }}\n" for x in range(3) for y in range(3))
       + "\t\tartillery_brigade = { x = 3 y = 0 }\n\t}\n\tsupport = {\n\t\tartillery = { x = 0 y = 0 }\n\t\tengineer = { x = 0 y = 1 }\n\t}\n}\n\nunits = {\n"
       + "\tdivision = {\n\t\tname = \"Tagma ton Athanaton\"\n\t\tlocation = 6995\n\t\tdivision_template = \"Athanatoi\"\n\t\tstart_experience_factor = 0.7\n\t\tstart_equipment_factor = 1.0\n\t}\n}\n")
open(J("history/units/X09_athanatoi.txt"), "w", encoding="utf-8", newline="\n").write(ath)

# ================= localisation =================
def q(t): return t.replace('"', '\\"')
L = ["l_english:", " # Byzantine Empire focus tree"]
for f in F:
    L.append(f' {f["id"]}:0 "{q(f["name"])}"'); L.append(f' {f["id"]}_desc:0 "{q(f["desc"])}"')
for key, _, _, name, desc in IDEAS:
    L.append(f' {key}:0 "{q(name)}"'); L.append(f' {key}_desc:0 "{q(desc)}"')
L += [f' {key}:0 "{q(name)}"' for key, name, _ in CHARS]
L += [
 ' X09_orthodox_league:0 "Orthodox League"',
 ' X09_roman_empire:0 "Roman Empire"', ' X09_roman_empire_ADJ:0 "Roman"', ' X09_roman_empire_DEF:0 "the Roman Empire"',
 ' byzantium.1.t:0 "A Roman Emperor in Constantinople"',
 ' byzantium.1.d:0 "Six centuries after the crusaders of Guillen III broke the old empire, and long after the Cumans left the City in ashes, a Roman emperor has ridden through the Golden Gate of Constantinople. The [From.GetNameDef] has taken the ruined city and declared it once more the capital of the Romans. In the shell of Hagia Sophia, the Ecumenical Patriarch\'s choir sang for the first time in living memory."',
 ' byzantium.1.a:0 "The City is ours."',
 ' byzantium.1.b:0 "The Byzantines are back on the Bosporus."',
]
L += EXTRA_LOC
open(J("localisation/english/X09_focus_l_english.yml"), "w", encoding="utf-8-sig", newline="\n").write("\n".join(L) + "\n")
print(len(F), "X09 focuses")
