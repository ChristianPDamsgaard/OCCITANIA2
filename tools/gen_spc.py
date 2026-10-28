# Generator for Aragon (SPC) focus tree, ideas and localisation.
import sys, os

REPO = sys.argv[1]

F = []  # focus dicts

def focus(id, x, y, icon, name, desc, cost=10, pre=None, excl=None, avail=None,
          bypass=None, effect="", ai=1, filters=None):
    F.append(dict(id=id, x=x, y=y, icon=icon, name=name, desc=desc, cost=cost,
                  pre=pre or [], excl=excl or [], avail=avail, bypass=bypass,
                  effect=effect, ai=ai, filters=filters or []))

# ---------- effect helpers ----------
def build(state, btype, level, slots=0):
    s = f"if = {{ limit = {{ {state} = {{ is_owned_and_controlled_by = ROOT }} }}\n"
    s += f"\t{state} = {{\n"
    if slots:
        s += f"\t\tadd_extra_state_shared_building_slots = {slots}\n"
    s += f"\t\tadd_building_construction = {{ type = {btype} level = {level} instant_build = yes }}\n"
    s += "\t}\n}\n"
    return s

def bunker(state, btype, level, sel):
    return (f"if = {{ limit = {{ {state} = {{ is_owned_and_controlled_by = ROOT }} }}\n"
            f"\t{state} = {{ add_building_construction = {{ type = {btype} level = {level} "
            f"province = {{ all_provinces = yes {sel} = yes }} instant_build = yes }} }}\n}}\n")

def tech(name, cat, bonus=0.5, uses=1):
    if cat.endswith("_doctrine"):
        return f"add_doctrine_cost_reduction = {{ name = {name} cost_reduction = 0.4 uses = {uses} category = {cat} }}\n"
    return f"add_tech_bonus = {{ name = {name} bonus = {bonus} uses = {uses} category = {cat} }}\n"

NOT_DEM = "NOT = { has_government = democratic }"
SUBJECTS_JOIN = ("every_subject_country = {\n\tlimit = { is_in_faction = no }\n"
                 "\tROOT = { add_to_faction = PREV }\n}\n")

# ======================= POLITICAL =======================
focus("SPC_the_bitter_peace", 29, 0, "GFX_goal_generic_national_unity", "The Bitter Peace",
      "Once Aragon was the greatest power on earth. Then came the ruinous wars for the Orient, Napoleon's fall, and a century of defeats at the hands of Provence and its upstart Empire of Occitania. Our last gamble, the joint war with Scandinavia, was saved from catastrophe only because the other powers forced Occitania to make peace. Aragon survives on the charity of foreigners. Before the Crown can rise again, its people must decide who will lead the reckoning.",
      cost=5, effect="add_political_power = 100\n", ai=50, filters=["FOCUS_FILTER_POLITICAL"])

# --- Fascist ---
focus("SPC_escotets_mandate", 24, 1, "GFX_goal_support_fascism", "Escotet's Mandate",
      "Carles Escotet seized power promising that Aragon would never again bow to Occitania. Now he must prove that the Moviment can deliver what the old order could not.",
      pre=[["SPC_the_bitter_peace"]], excl=["SPC_whispers_in_the_palace", "SPC_voices_of_the_corts"],
      avail="has_government = fascism",
      effect="add_political_power = 75\nadd_popularity = { ideology = fascism popularity = 0.05 }\n",
      ai=20, filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_unify_the_moviment", 24, 2, "GFX_goal_generic_political_pressure", "Unify the Moviment",
      "The Moviment is a quarrelsome coalition of veterans, syndicalists and monarchists. Escotet will bind its factions into a single instrument of national will.",
      pre=[["SPC_escotets_mandate"]],
      effect="add_stability = 0.05\nadd_popularity = { ideology = fascism popularity = 0.05 }\nadd_political_power = 50\n",
      filters=["FOCUS_FILTER_POLITICAL", "FOCUS_FILTER_STABILITY"])
focus("SPC_black_shirts_of_saragossa", 22, 3, "GFX_goal_generic_allies_build_infantry", "The Black Shirts of Saragossa",
      "The street fighters of Saragossa carried Escotet to power. Organised into a national militia, they will guard the regime at home while the army looks abroad.",
      pre=[["SPC_unify_the_moviment"]], effect="add_ideas = SPC_saragossa_militia\n",
      filters=["FOCUS_FILTER_STABILITY", "FOCUS_FILTER_MANPOWER"])
focus("SPC_purge_the_defeatists", 24, 3, "GFX_goal_generic_fortify_city", "Purge the Defeatists",
      "Those who signed the shameful peace treaties still sit in our ministries and officer messes. They will be removed, and the wound of defeat will become a fire of vengeance.",
      pre=[["SPC_unify_the_moviment"]],
      effect="remove_ideas = SPC_wounds_of_defeat\nadd_ideas = SPC_revanchist_fervor\nadd_stability = -0.05\n",
      filters=["FOCUS_FILTER_WAR_SUPPORT"])
focus("SPC_ministry_of_national_spirit", 26, 3, "GFX_goal_generic_propaganda", "Ministry of National Spirit",
      "Newspapers, radio and cinema will speak with one voice: the voice of an Aragon that remembers what was taken from it.",
      pre=[["SPC_unify_the_moviment"]],
      effect="add_war_support = 0.1\nadd_popularity = { ideology = fascism popularity = 0.05 }\n",
      filters=["FOCUS_FILTER_WAR_SUPPORT"])
focus("SPC_the_corporate_state", 23, 4, "GFX_goal_generic_production", "The Corporate State",
      "Employers and workers will be bound together in state syndicates, ending strikes and directing every factory toward the needs of the nation.",
      pre=[["SPC_black_shirts_of_saragossa"], ["SPC_purge_the_defeatists"]],
      effect="add_ideas = SPC_corporate_state\n", filters=["FOCUS_FILTER_INDUSTRY"])
focus("SPC_aragonese_youth_front", 25, 4, "GFX_goal_generic_special_forces", "The Aragonese Youth Front",
      "The generation that grew up under defeat will be the generation that avenges it. Every boy in Aragon will learn to march, to shoot and to remember.",
      pre=[["SPC_ministry_of_national_spirit"]],
      effect="add_manpower = 25000\narmy_experience = 10\n", filters=["FOCUS_FILTER_MANPOWER", "FOCUS_FILTER_ARMY_XP"])
focus("SPC_the_cabdills_cult", 24, 5, "GFX_goal_generic_national_unity", "The Cult of the Cabdill",
      "Escotet is no longer merely a politician. He is the Cabdill, the leader who embodies the Aragonese nation and its destiny.",
      pre=[["SPC_the_corporate_state"], ["SPC_aragonese_youth_front"]],
      effect="add_political_power = 150\nadd_stability = 0.1\n", filters=["FOCUS_FILTER_POLITICAL", "FOCUS_FILTER_STABILITY"])
focus("SPC_total_mobilization", 23, 6, "GFX_goal_generic_construct_mil_factory", "Total Mobilisation",
      "Peace was only ever a pause between wars. The economy of the Crown will be placed on a permanent war footing.",
      pre=[["SPC_the_cabdills_cult"]], avail="has_war_support > 0.5",
      effect="add_ideas = war_economy\nadd_war_support = 0.05\n", filters=["FOCUS_FILTER_INDUSTRY"])
focus("SPC_the_new_aragonese_order", 25, 6, "GFX_goal_generic_military_sphere", "The New Aragonese Order",
      "Aragon will not fight alone. The Pact of Saragossa will bind our dominions and like-minded states into a bloc that Occitania cannot break.",
      pre=[["SPC_the_cabdills_cult"]],
      effect=("if = { limit = { is_in_faction = no }\n\tcreate_faction_from_template = { template = faction_template_fascism name = SPC_pact_of_saragossa }\n}\n" + SUBJECTS_JOIN +
              "add_political_power = 50\n"),
      filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_aragon_above_all", 24, 7, "GFX_goal_generic_major_war", "Aragon Above All",
      "The nation is reborn, the army is ready and the people are united. All that remains is to take back what is ours.",
      pre=[["SPC_total_mobilization"], ["SPC_the_new_aragonese_order"]],
      effect="add_ideas = SPC_aragon_above_all\n", filters=["FOCUS_FILTER_WAR_SUPPORT"])

# --- Absolutist ---
focus("SPC_whispers_in_the_palace", 29, 1, "GFX_focus_hun_elect_a_king", "Whispers in the Palace",
      "In the shuttered halls of the Aljafería, generals and grandees speak quietly of the exiled royal house. Escotet promised glory and delivered only more defeats.",
      pre=[["SPC_the_bitter_peace"]], excl=["SPC_escotets_mandate", "SPC_voices_of_the_corts"],
      effect="add_popularity = { ideology = absolutist popularity = 0.15 }\nadd_political_power = 50\n",
      ai=4, filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_the_officers_plot", 29, 2, "GFX_goal_generic_army_doctrines", "The Officers' Plot",
      "The officer corps never forgave Escotet for the purges of its ranks. A conspiracy of colonels now waits only for the word of the rightful king.",
      pre=[["SPC_whispers_in_the_palace"]],
      effect="add_popularity = { ideology = absolutist popularity = 0.15 }\narmy_experience = 10\n",
      filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_the_crown_reclaimed", 29, 3, "GFX_focus_rom_royal_dictatorship", "The Crown Reclaimed",
      "At dawn the army seizes the ministries and Escotet is put on a ship into exile. Jaume V enters Saragossa to the sound of church bells. The Crown of Aragon lives again.",
      pre=[["SPC_the_officers_plot"]], excl=["SPC_the_eagle_returns"],
      avail="absolutist > 0.25\nhas_war = no",
      effect=("set_politics = { ruling_party = absolutist elections_allowed = no }\n"
              "set_popularities = { absolutist = 55 fascism = 30 democratic = 10 neutrality = 5 }\n"
              "recruit_character = SPC_jaume_v\npromote_character = SPC_jaume_v\n"
              "retire_character = SPC_carles_escotet\n"
              "remove_ideas = SPC_wounds_of_defeat\nadd_ideas = SPC_crown_of_aragon\n"),
      filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_the_eagle_returns", 31, 3, "GFX_focus_hun_elect_a_king", "The Eagle Returns",
      "Some conspirators want the old House of Barcelona; others remember that Aragon's last age of glory came under Napoleon, the Corsican who made Aragon master of Europe. His great-grandnephew, Napoleó IV Bonaparte, is ready to take up the imperial crown.",
      pre=[["SPC_the_officers_plot"]], excl=["SPC_the_crown_reclaimed"],
      avail="absolutist > 0.25\nhas_war = no",
      effect=("set_politics = { ruling_party = absolutist elections_allowed = no }\n"
              "set_popularities = { absolutist = 55 fascism = 30 democratic = 10 neutrality = 5 }\n"
              "recruit_character = SPC_napoleo_iv\npromote_character = SPC_napoleo_iv\n"
              "retire_character = SPC_carles_escotet\n"
              "set_cosmetic_tag = SPC_bonapartist\n"
              "remove_ideas = SPC_wounds_of_defeat\nadd_ideas = SPC_imperial_eagle\n"),
      filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_the_royal_council", 28, 4, "GFX_goal_generic_political_pressure", "The Royal Council",
      "The king will govern through a council of nobles, bishops and marshals: men of tradition who know that a nation is built on loyalty, not slogans.",
      pre=[["SPC_the_crown_reclaimed", "SPC_the_eagle_returns"]], effect="add_ideas = SPC_royal_council\n",
      filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_restore_the_usatges", 30, 4, "GFX_focus_generic_treaty", "Restore the Usatges",
      "The ancient Usatges of Barcelona bound king and subject in mutual obligation. Restoring them reminds every Aragonese that the Crown is older than any party.",
      pre=[["SPC_the_crown_reclaimed", "SPC_the_eagle_returns"]],
      effect="add_stability = 0.1\nadd_political_power = 75\n", filters=["FOCUS_FILTER_STABILITY"])
focus("SPC_a_noble_officer_corps", 28, 5, "GFX_goal_generic_army_doctrines", "A Noble Officer Corps",
      "The sons of the great houses will once more lead the king's armies, as their ancestors did at Muret and Palermo.",
      pre=[["SPC_the_royal_council"]],
      effect="army_experience = 25\n" + tech("SPC_a_noble_officer_corps", "land_doctrine", 0.5, 1),
      filters=["FOCUS_FILTER_ARMY_XP", "FOCUS_FILTER_RESEARCH"])
focus("SPC_the_mediterranean_crown", 30, 5, "GFX_goal_generic_navy_doctrines_tactics", "The Mediterranean Crown",
      "Montpellier and Provence once owed homage to the Crown of Aragon. Provence repaid that debt by building the empire that humbled us. The Crown remembers its old rights, even if Occitania pretends to forget them.",
      pre=[["SPC_restore_the_usatges"]],
      effect="add_state_claim = 574\nadd_state_claim = 566\nnavy_experience = 25\n",
      filters=["FOCUS_FILTER_ANNEXATION", "FOCUS_FILTER_NAVY_XP"])
focus("SPC_alliance_of_crowns", 29, 6, "GFX_focus_generic_treaty", "The Alliance of Crowns",
      "Thrones must stand together against the tide of republicans and demagogues. The Crown of Aragon will gather its dominions into a royal alliance.",
      pre=[["SPC_a_noble_officer_corps"], ["SPC_the_mediterranean_crown"]],
      effect=("if = { limit = { is_in_faction = no }\n\tcreate_faction_from_template = { template = faction_template_absolutist name = SPC_alliance_of_crowns }\n}\n" + SUBJECTS_JOIN +
              "add_political_power = 50\n"),
      filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_the_second_conqueror", 29, 7, "GFX_goal_generic_major_war", "The Second Conqueror",
      "Jaume I won Majorca and Valencia and earned the name of Conqueror. His descendant intends to earn it again.",
      pre=[["SPC_alliance_of_crowns"]], effect="add_ideas = SPC_second_conqueror\n",
      filters=["FOCUS_FILTER_WAR_SUPPORT"])

# --- Democratic ---
focus("SPC_voices_of_the_corts", 33, 1, "GFX_goal_support_democracy", "Voices of the Corts",
      "The Corts were silenced when Escotet took power, but their deputies never stopped meeting in cellars and cafes. Now their pamphlets are everywhere.",
      pre=[["SPC_the_bitter_peace"]], excl=["SPC_escotets_mandate", "SPC_whispers_in_the_palace"],
      effect="add_popularity = { ideology = democratic popularity = 0.15 }\n",
      ai=1, filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_the_valencia_manifesto", 33, 2, "GFX_goal_generic_propaganda", "The Valencia Manifesto",
      "From Valencia, a coalition of liberals, socialists and regionalists publishes its demands: free elections, a free press and an end to the Cabdill's wars.",
      pre=[["SPC_voices_of_the_corts"]],
      effect="add_popularity = { ideology = democratic popularity = 0.2 }\nadd_stability = -0.05\n",
      filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_the_fall_of_escotet", 33, 3, "GFX_goal_generic_territory_or_war", "The Fall of Escotet",
      "General strikes paralyse the cities and the garrisons refuse to fire on the crowds. Escotet's government collapses, but his black shirts will not surrender without a fight.",
      pre=[["SPC_the_valencia_manifesto"]],
      avail="democratic > 0.25\nhas_war = no",
      effect=("set_politics = { ruling_party = democratic elections_allowed = yes last_election = \"1936.1.1\" election_frequency = 48 }\n"
              "set_popularities = { democratic = 55 fascism = 35 absolutist = 5 neutrality = 5 }\n"
              "recruit_character = SPC_josep_ferrer\npromote_character = SPC_josep_ferrer\n"
              "start_civil_war = { ideology = fascism size = 0.35 }\n"),
      filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_truth_and_reconciliation", 32, 4, "GFX_goal_generic_national_unity", "Truth and Reconciliation",
      "The republic will not build itself on new purges. Former enemies will be offered amnesty, and the nation will finally mourn its defeats instead of feeding on them.",
      pre=[["SPC_the_fall_of_escotet"]], avail="has_civil_war = no",
      effect="remove_ideas = SPC_wounds_of_defeat\nadd_stability = 0.1\n", filters=["FOCUS_FILTER_STABILITY"])
focus("SPC_free_corts_elections", 34, 4, "GFX_goal_support_democracy", "Free Elections to the Corts",
      "For the first time in a generation, Aragonese citizens will choose their own deputies.",
      pre=[["SPC_the_fall_of_escotet"]], avail="has_civil_war = no",
      effect="add_ideas = SPC_free_corts\n", filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_an_army_of_citizens", 32, 5, "GFX_goal_generic_allies_build_infantry", "An Army of Citizens",
      "The army that served the Cabdill must learn to serve the republic. Purged of political officers, it will be smaller, better trained and loyal to the constitution.",
      pre=[["SPC_truth_and_reconciliation"]],
      effect="army_experience = 15\n" + tech("SPC_an_army_of_citizens", "land_doctrine", 0.5, 1),
      filters=["FOCUS_FILTER_ARMY_XP", "FOCUS_FILTER_RESEARCH"])
focus("SPC_open_the_markets", 34, 5, "GFX_goal_generic_trade", "Open the Markets",
      "Autarky impoverished Aragon. The republic will trade with the world and let prosperity rebuild what war destroyed.",
      pre=[["SPC_free_corts_elections"]],
      effect="add_ideas = free_trade\nadd_political_power = 50\n", filters=["FOCUS_FILTER_INDUSTRY"])
focus("SPC_rapprochement_with_catalonia", 32, 6, "GFX_focus_generic_treaty", "Rapprochement with Catalonia",
      "Catalonia took our northern provinces, but it too fears Occitan power. Old enemies may yet become partners.",
      pre=[["SPC_an_army_of_citizens"]], avail="country_exists = CAT\nNOT = { has_war_with = CAT }",
      effect=("add_opinion_modifier = { target = CAT modifier = positive_50 }\n"
              "CAT = { add_opinion_modifier = { target = ROOT modifier = positive_50 } }\n"
              "diplomatic_relation = { country = CAT relation = non_aggression_pact }\n"),
      filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_the_middle_sea_entente", 34, 6, "GFX_goal_generic_military_sphere", "The Middle Sea Entente",
      "A free Aragon will stand with the free peoples of Europe. Our old friends in Scandinavia are invited to join a defensive entente against Occitan aggression.",
      pre=[["SPC_open_the_markets"]],
      effect=("if = { limit = { is_in_faction = no }\n\tcreate_faction_from_template = { template = faction_template_defensive_democratic name = SPC_middle_sea_entente }\n}\n" + SUBJECTS_JOIN +
              "if = { limit = { country_exists = SCA SCA = { is_in_faction = no has_government = democratic } }\n"
              "\tadd_to_faction = SCA\n}\n"),
      filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_collective_security", 33, 7, "GFX_goal_generic_defence", "Collective Security",
      "If Occitania threatens the peace of the Middle Sea again, the Entente will answer together, and this time the lost provinces will be freed.",
      pre=[["SPC_rapprochement_with_catalonia"], ["SPC_the_middle_sea_entente"]],
      avail="threat > 0.4\ncountry_exists = OCC",
      effect=("add_ideas = SPC_collective_security\n"
              "create_wargoal = { type = take_core_state target = OCC generator = { 567 580 581 } }\n"),
      filters=["FOCUS_FILTER_WAR_SUPPORT"])

# ======================= REVANCHE =======================
focus("SPC_the_lost_provinces", 40, 1, "GFX_goal_generic_more_territorial_claims", "The Lost Provinces",
      "Corsica, Limousin and Poitou in Occitan hands. Paris and the Loire under Catalonia. Kent under England. Every schoolchild in Aragon can recite the list.",
      pre=[["SPC_the_bitter_peace"]],
      effect="add_war_support = 0.05\nadd_political_power = 50\n", filters=["FOCUS_FILTER_WAR_SUPPORT"])
focus("SPC_fortify_the_pyrenean_line", 38, 2, "GFX_goal_generic_defence", "Fortify the Pyrenean Line",
      "Before Aragon can strike, it must be certain it will not be struck. The passes of the Pyrenees will be sealed with concrete and steel.",
      pre=[["SPC_the_lost_provinces"]],
      effect=bunker(30, "bunker", 2, "limit_to_border") + bunker(68, "bunker", 2, "limit_to_border"),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("SPC_a_debt_written_in_blood", 42, 2, "GFX_goal_generic_major_war", "A Debt Written in Blood",
      "Aragon's enemies wrote the peace treaties in our blood. That debt will be repaid in kind.",
      pre=[["SPC_the_lost_provinces"]], avail=NOT_DEM,
      effect="add_war_support = 0.1\n", filters=["FOCUS_FILTER_WAR_SUPPORT"])
focus("SPC_renew_the_scandinavian_pact", 40, 2, "GFX_focus_generic_treaty", "Renew the Scandinavian Pact",
      "Scandinavia marched with us in the last war, striking Occitania from the north while we attacked from the south. That alliance nearly worked. It must be renewed.",
      pre=[["SPC_the_lost_provinces"]], avail="country_exists = SCA\nNOT = { has_war_with = SCA }",
      effect=("add_opinion_modifier = { target = SCA modifier = positive_50 }\n"
              "SCA = { add_opinion_modifier = { target = ROOT modifier = positive_50 } }\n"
              "if = { limit = { is_faction_leader = yes SCA = { is_in_faction = no } }\n\tadd_to_faction = SCA\n}\n"
              "else_if = { limit = { is_in_faction = no SCA = { is_in_faction = no } }\n"
              "\tcreate_faction_from_template = { template = faction_template_generic name = SPC_northern_pact }\n\tadd_to_faction = SCA\n}\n"),
      filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_the_pincer_plan", 40, 4, "GFX_goal_generic_position_armies", "The Pincer Plan",
      "The two-pronged attack failed last time because Aragon's prong broke first. Joint staff talks with Stockholm will make sure that does not happen again.",
      pre=[["SPC_renew_the_scandinavian_pact"]], avail="SCA = { is_in_faction_with = ROOT }",
      effect="add_ideas = SPC_pincer_plan\narmy_experience = 15\n",
      filters=["FOCUS_FILTER_ARMY_XP"])
focus("SPC_the_corsican_question", 37, 3, "GFX_goal_generic_occupy_states_ongoing_war", "The Corsican Question",
      "Corsica gave Aragon its greatest son: Napoleon, Emperor of Aragon, born in Ajaccio. That his island now flies the Occitan flag is an insult no Aragonese can forgive. It also guards the sea lanes between Sardinia and our Italian provinces.",
      pre=[["SPC_fortify_the_pyrenean_line"]], avail=NOT_DEM + "\ncountry_exists = OCC",
      bypass="567 = { is_owned_by = ROOT }",
      effect="create_wargoal = { type = take_core_state target = OCC generator = { 567 } }\n",
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("SPC_the_march_on_rome", 39, 3, "GFX_goal_generic_demand_territory", "The March on Rome",
      "Our legions hold Naples and Venice, yet the Eternal City lies in Occitan hands. Rome must become Aragonese.",
      pre=[["SPC_fortify_the_pyrenean_line"]], avail=NOT_DEM + "\ncountry_exists = OCC",
      bypass="572 = { is_owned_by = ROOT }",
      effect=("add_state_claim = 572\n"
              "if = { limit = { 572 = { is_owned_by = OCC } }\n\tcreate_wargoal = { type = take_state_focus target = OCC generator = { 572 } }\n}\n"),
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("SPC_the_road_to_paris", 41, 3, "GFX_goal_generic_occupy_states_ongoing_war", "The Road to Paris",
      "Catalonia's capture of Paris and the Loire was the deepest humiliation of the last war. The road north must be reopened.",
      pre=[["SPC_a_debt_written_in_blood"]], avail=NOT_DEM + "\ncountry_exists = CAT",
      effect="create_wargoal = { type = take_core_state target = CAT generator = { 106 109 110 111 } }\n",
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("SPC_unfinished_business_in_england", 43, 3, "GFX_goal_generic_amphibious_assault", "Unfinished Business in England",
      "We hold Ireland, Scotland and Wales, but the English still sit in Kent. The isles will be whole under the Crown.",
      pre=[["SPC_a_debt_written_in_blood"]], avail=NOT_DEM + "\ncountry_exists = X20",
      effect="create_wargoal = { type = take_core_state target = X20 generator = { 226 } }\n",
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("SPC_the_war_of_revanche", 38, 4, "GFX_goal_generic_territory_or_war", "The War of Revanche",
      "In the last war Aragon was nearly overrun and was saved only by foreign threats. This time no one will need to save us. Aragon marches on Occitania to take back what was stolen.",
      pre=[["SPC_the_corsican_question"], ["SPC_the_march_on_rome"]],
      avail=NOT_DEM + "\ncountry_exists = OCC\nNOT = { has_war_with = OCC }",
      effect=("declare_war_on = { target = OCC type = take_core_state generator = { 567 580 581 } }\n"
              "add_named_threat = { threat = 2 name = SPC_revanche_threat }\n"),
      ai=3, filters=["FOCUS_FILTER_ANNEXATION"])
focus("SPC_break_the_occitan_hegemony", 38, 5, "GFX_goal_anschluss", "Break the Occitan Hegemony",
      "Occitania's armies are broken. Its southern provinces, long tied to Aragon by blood and trade, will never again be used as a springboard against us.",
      pre=[["SPC_the_war_of_revanche"]],
      avail="OR = { OCC = { has_capitulated = yes } controls_state = 566 }",
      effect=("add_state_claim = 566\nadd_state_claim = 574\nadd_state_claim = 576\nadd_state_claim = 579\n"
              "add_stability = 0.1\nadd_political_power = 100\n"),
      filters=["FOCUS_FILTER_ANNEXATION"])

# ======================= EAST =======================
focus("SPC_the_eastern_dominions", 47, 1, "GFX_goal_generic_construct_infrastructure", "The Eastern Dominions",
      "Greece, the Balkans and Anatolia are the Crown's newest and least loyal lands. Roads and garrisons will tie them to Saragossa.",
      pre=[["SPC_the_bitter_peace"]],
      effect=build(47, "infrastructure", 1) + build(49, "infrastructure", 1) + "add_stability = 0.05\n",
      filters=["FOCUS_FILTER_INDUSTRY", "FOCUS_FILTER_STABILITY"])
focus("SPC_the_anatolian_mines", 46, 2, "GFX_goal_generic_construction2", "The Anatolian Mines",
      "The hills of Aydin and Konya hide chromium and iron that our factories badly need.",
      pre=[["SPC_the_eastern_dominions"]],
      effect=("if = { limit = { 55 = { is_owned_by = ROOT } } add_resource = { type = chromium amount = 8 state = 55 } }\n"
              "if = { limit = { 54 = { is_owned_by = ROOT } } add_resource = { type = steel amount = 8 state = 54 } }\n"),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("SPC_athens_and_neopatria", 48, 2, "GFX_goal_generic_national_unity", "Athens and Neopatria",
      "The Catalan Company ruled the Duchies of Athens and Neopatria six centuries ago. With Thessaly and Western Macedonia taken from the Byzantines, the old duchies can be restored to the Crown.",
      pre=[["SPC_the_eastern_dominions"]],
      avail="99 = { is_owned_by = ROOT }\n100 = { is_owned_by = ROOT }",
      effect="add_state_core = 99\nadd_state_core = 100\nadd_stability = 0.05\n",
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("SPC_the_byzantine_question", 48, 3, "GFX_goal_generic_demand_territory", "The Byzantine Question",
      "In exchange for Thessaly the Byzantines were handed Kastamonu and Ankara, and now they eye Attica and the Aegean as well. It is time to take back the Anatolian provinces and end the Byzantine remnant's ambitions.",
      pre=[["SPC_athens_and_neopatria"]], avail=NOT_DEM + "\ncountry_exists = X09",
      effect=("add_state_claim = 56\nadd_state_claim = 63\n"
              "create_wargoal = { type = take_state_focus target = X09 generator = { 56 63 } }\n"),
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("SPC_pacify_the_highlands", 46, 3, "GFX_goal_generic_allies_build_infantry", "Pacify the Highlands",
      "The mountain clans of Albania and Montenegro have never truly accepted Aragonese rule. Roads, schools and garrisons will change that, and their warriors will fill our regiments.",
      pre=[["SPC_the_anatolian_mines"]],
      effect=build(51, "infrastructure", 1) + build(45, "infrastructure", 1) + "add_manpower = 15000\n",
      filters=["FOCUS_FILTER_MANPOWER"])

focus("SPC_suppress_the_hetairists", 46, 4, "GFX_goal_generic_fortify_city", "Suppress the Hetairists",
      "Greek secret societies are smuggling rifles into Salonika and Athens and preaching revolt in every village. The gendarmerie will break them before they are ready to strike.",
      pre=[["SPC_pacify_the_highlands"]],
      effect=("set_country_flag = SPC_hetairists_suppressed\nadd_stability = 0.05\n"
              "if = { limit = { country_exists = GRE } GRE = { add_war_support = -0.1 } }\n"),
      ai=5, filters=["FOCUS_FILTER_STABILITY"])
# ======================= COLONIAL =======================
focus("SPC_the_african_dominions", 50, 1, "GFX_focus_eng_move_to_secure_the_dominions", "The African Dominions",
      "From Western Sahara to São Tomé, the dominions of the Crown stood by Aragon when Europe abandoned it. Their loyalty will be rewarded.",
      pre=[["SPC_the_bitter_peace"]],
      effect=("every_subject_country = { add_opinion_modifier = { target = ROOT modifier = positive_50 } }\n"
              "add_political_power = 50\n"), filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_colonial_levies", 50, 2, "GFX_goal_generic_allies_build_infantry", "Colonial Levies",
      "The dominions will raise regiments for the Crown. In return, their veterans will be granted Aragonese citizenship.",
      pre=[["SPC_the_african_dominions"]],
      effect="add_manpower = 25000\n", filters=["FOCUS_FILTER_MANPOWER"])

# ======================= THE ORIENT =======================
focus("SPC_the_dream_of_the_orient", 54, 1, "GFX_goal_generic_major_war", "The Dream of the Orient",
      "For three centuries Aragonese kings chased the glory of Alexander and Caesar in the East, and for three centuries the East swallowed our armies. The dream drained the treasury that once made Aragon the world's greatest power. Now Aragon must decide: revive it, or bury it for good.",
      pre=[["SPC_the_bitter_peace"]], effect="add_political_power = 50\n", filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_heirs_of_alexander", 52, 2, "GFX_goal_generic_demand_territory", "Heirs of Alexander",
      "Our ancestors failed because they were half-hearted. Modern armies, railways and steamships will succeed where galleys and pikes did not. The Orient will be ours.",
      pre=[["SPC_the_dream_of_the_orient"]], excl=["SPC_bury_the_oriental_dream"], avail=NOT_DEM,
      effect="add_ideas = SPC_heirs_of_alexander\n", ai=2, filters=["FOCUS_FILTER_WAR_SUPPORT"])
focus("SPC_cyprus_and_the_levantine_sea", 51, 3, "GFX_goal_generic_amphibious_assault", "Cyprus and the Levantine Sea",
      "Every eastern crusade of the Crown began at Cyprus. The Ilkhanate holds it now.",
      pre=[["SPC_heirs_of_alexander"]], avail="country_exists = X63",
      bypass="767 = { is_owned_by = ROOT }",
      effect="add_state_claim = 767\ncreate_wargoal = { type = take_state_focus target = X63 generator = { 767 } }\n",
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("SPC_caesars_road_to_alexandria", 53, 3, "GFX_goal_generic_occupy_states_ongoing_war", "Caesar's Road to Alexandria",
      "Caesar took Egypt and made himself master of the Middle Sea. The Baruun Khanate's grip on the Nile is weaker than it looks.",
      pre=[["SPC_heirs_of_alexander"]], avail="country_exists = X65",
      bypass="803 = { is_owned_by = ROOT }",
      effect=("add_state_claim = 803\nadd_state_claim = 804\n"
              "create_wargoal = { type = take_state_focus target = X65 generator = { 803 804 } }\n"),
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("SPC_the_crusader_compact", 51, 4, "GFX_focus_generic_treaty", "The Crusader Compact",
      "The Kingdom of Jerusalem is a Christian island in a Mongol sea. It needs a protector, and Aragon needs a foothold in the Holy Land.",
      pre=[["SPC_cyprus_and_the_levantine_sea"]], avail="country_exists = X27\nNOT = { has_war_with = X27 }",
      effect=("add_opinion_modifier = { target = X27 modifier = positive_50 }\n"
              "X27 = { add_opinion_modifier = { target = ROOT modifier = positive_50 } }\n"
              "give_guarantee = X27\n"),
      filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_the_march_of_alexander", 53, 4, "GFX_goal_generic_territory_or_war", "The March of Alexander",
      "From the Nile, Alexander marched to Mesopotamia. Mosul and Baghdad, the jewels of the Ilkhanate, will mark the end of our road.",
      pre=[["SPC_caesars_road_to_alexandria"]], avail="country_exists = X63\n803 = { is_owned_by = ROOT }",
      effect=("add_state_claim = 773\nadd_state_claim = 774\n"
              "create_wargoal = { type = take_state_focus target = X63 generator = { 773 774 } }\n"),
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("SPC_where_our_fathers_failed", 52, 5, "GFX_goal_generic_national_unity", "Where Our Fathers Failed",
      "The Orient that ruined Aragon now bows to it. Three centuries of failure have been redeemed.",
      pre=[["SPC_the_crusader_compact"], ["SPC_the_march_of_alexander"]],
      avail="803 = { is_owned_by = ROOT }\n767 = { is_owned_by = ROOT }",
      effect=("remove_ideas = SPC_heirs_of_alexander\nadd_ideas = SPC_alexanders_legacy\n"
              "add_state_core = 767\nadd_state_core = 803\nadd_political_power = 150\n"),
      filters=["FOCUS_FILTER_ANNEXATION", "FOCUS_FILTER_WAR_SUPPORT"])
focus("SPC_bury_the_oriental_dream", 56, 2, "GFX_goal_generic_neutrality_focus", "Bury the Oriental Dream",
      "The East made fools of twenty kings. Aragon's future and its lost provinces lie in Europe, not in the deserts of the Levant.",
      pre=[["SPC_the_dream_of_the_orient"]], excl=["SPC_heirs_of_alexander"],
      effect="add_ideas = SPC_europe_first\nadd_stability = 0.05\n", ai=3, filters=["FOCUS_FILTER_STABILITY"])
focus("SPC_trade_not_conquest", 55, 3, "GFX_goal_generic_trade", "Trade, Not Conquest",
      "What our armies never won, our merchants can. Smyrna will become the Crown's gateway to the Levant trade.",
      pre=[["SPC_bury_the_oriental_dream"]],
      effect=build(54, "industrial_complex", 1, 1) + build(54, "dockyard", 1) + "add_political_power = 50\n",
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("SPC_bring_the_legions_home", 57, 3, "GFX_goal_generic_allies_build_infantry", "Bring the Legions Home",
      "The garrisons scattered across Anatolia and the islands will come home to guard the Pyrenees.",
      pre=[["SPC_bury_the_oriental_dream"]],
      effect="add_manpower = 30000\narmy_experience = 15\n", filters=["FOCUS_FILTER_MANPOWER", "FOCUS_FILTER_ARMY_XP"])
focus("SPC_eyes_on_the_pyrenees", 56, 4, "GFX_goal_generic_defence", "Eyes on the Pyrenees",
      "Every soldier, every peseta and every ship is now committed to one goal: the lost provinces.",
      pre=[["SPC_trade_not_conquest"], ["SPC_bring_the_legions_home"]],
      effect="remove_ideas = SPC_europe_first\nadd_ideas = SPC_eyes_on_the_pyrenees\n",
      filters=["FOCUS_FILTER_WAR_SUPPORT"])

# ======================= TRIPLE MONARCHY =======================
focus("SPC_the_legacy_of_guillen_iv", 60, 1, "GFX_focus_hun_elect_a_king", "The Legacy of Guillen IV",
      "King Guillen IV led Aragon's own crusade, drove the Turks out of France, then pressed his claim to the English throne. Crowned Emperor of the Triple Monarchy, he ruled Aragon, France and England as one. Restoring his empire would undo every humiliation since.",
      pre=[["SPC_the_bitter_peace"]], avail=NOT_DEM,
      effect="add_war_support = 0.05\nadd_political_power = 50\ncustom_effect_tooltip = SPC_unlock_triple_monarchy_tt\n",
      filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_the_french_inheritance", 59, 2, "GFX_goal_generic_more_territorial_claims", "The French Inheritance",
      "Guillen's crusaders, not the Catalans, freed France from the Turks. Normandy, Brittany and Champagne belong to his heirs.",
      pre=[["SPC_the_legacy_of_guillen_iv"]],
      effect=("add_state_claim = 105\nadd_state_claim = 107\nadd_state_claim = 108\nadd_state_claim = 112\nadd_state_claim = 123\n"
              "add_war_support = 0.05\n"),
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("SPC_guillens_english_claim", 61, 2, "GFX_goal_generic_amphibious_assault", "Guillen's English Claim",
      "Guillen was crowned in London by right of blood, and his line has never renounced that right. The English heartland will answer to the Triple Crown again.",
      pre=[["SPC_the_legacy_of_guillen_iv"]], avail="country_exists = X20",
      effect=("add_state_claim = 227\nadd_state_claim = 245\n"
              "create_wargoal = { type = take_state_focus target = X20 generator = { 227 245 } }\n"),
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("SPC_the_imperial_regalia", 59, 3, "GFX_goal_generic_national_unity", "The Imperial Regalia",
      "The three crowns of Guillen IV lie in the treasury of Saragossa, unworn for a century. They will be brought out and shown to the people.",
      pre=[["SPC_the_french_inheritance"]],
      effect="add_political_power = 100\nadd_stability = 0.05\n", filters=["FOCUS_FILTER_POLITICAL"])
focus("SPC_the_northern_english_counties", 61, 3, "GFX_goal_generic_construct_infrastructure", "The Northern English Counties",
      "We already rule Yorkshire and Lancashire. Aragonese schools, courts and railways will make their people subjects of the Triple Crown in spirit as well as law.",
      pre=[["SPC_guillens_english_claim"]], avail="64 = { is_owned_by = ROOT }\n66 = { is_owned_by = ROOT }",
      effect="add_state_core = 64\nadd_state_core = 66\n" + build(64, "infrastructure", 1) + build(66, "infrastructure", 1),
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("SPC_emperor_of_three_crowns", 60, 4, "GFX_focus_rom_royal_dictatorship", "Emperor of Three Crowns",
      "Aragon, France and England are united once more under one emperor. The world's first superpower has returned.",
      pre=[["SPC_the_imperial_regalia"], ["SPC_the_northern_english_counties"]],
      avail="has_country_flag = SPC_triple_monarchy_formed",
      effect="add_ideas = SPC_emperor_of_three_crowns\nadd_political_power = 100\n", filters=["FOCUS_FILTER_WAR_SUPPORT"])

# ======================= INDUSTRY =======================
focus("SPC_the_plan_of_restoration", 3, 0, "GFX_goal_generic_production", "The Plan of Restoration",
      "Defeat has left our factories idle and our treasury empty. A national plan will rebuild Aragonese industry from the ground up.",
      effect="add_ideas = SPC_plan_of_restoration\n" + build(30, "industrial_complex", 1, 1), ai=20,
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("SPC_rebuild_the_heartland", 1, 1, "GFX_goal_generic_construct_civ_factory", "Rebuild the Heartland",
      "Aragon is still a land of peasants and vineyards; its few factories cluster in Valencia and Catalonia. Their workshops will be the first to grow, and the first to draw labour from the countryside.",
      pre=[["SPC_the_plan_of_restoration"]],
      effect=("remove_ideas = SPC_agrarian_society\nadd_ideas = SPC_agrarian_society_2\n" +
              build(65, "industrial_complex", 1, 1) + build(68, "industrial_complex", 1, 1)),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("SPC_the_italian_workshops", 3, 1, "GFX_goal_generic_construct_civ_factory", "The Italian Workshops",
      "Naples and Apulia are home to millions of skilled hands. Investment in the south of Italy will turn them toward the Crown's needs.",
      pre=[["SPC_the_plan_of_restoration"]],
      effect=build(38, "industrial_complex", 1, 1) + build(37, "industrial_complex", 1, 1),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("SPC_roads_of_the_crown", 5, 1, "GFX_goal_generic_construct_infrastructure", "Roads of the Crown",
      "An empire scattered across the Middle Sea must move men and goods quickly between its provinces.",
      pre=[["SPC_the_plan_of_restoration"]],
      effect=build(30, "infrastructure", 1) + build(65, "infrastructure", 1) + build(38, "infrastructure", 1),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("SPC_the_arsenal_of_saragossa", 1, 2, "GFX_goal_generic_construct_mil_factory", "The Arsenal of Saragossa",
      "The capital's great arsenal will be expanded to arm the legions of the revanche.",
      pre=[["SPC_rebuild_the_heartland"]], effect=build(30, "arms_factory", 2, 2),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("SPC_the_royal_academies", 3, 2, "GFX_focus_research", "The Royal Academies of Science",
      "The scholars of Valencia, Naples and Athens will be organised into royal academies serving the state.",
      pre=[["SPC_the_italian_workshops"]], effect="add_research_slot = 1\n",
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_industrialise_the_northern_isles", 5, 2, "GFX_goal_generic_construct_civ_factory", "Industrialise the Northern Isles",
      "Ireland and the Scottish Lowlands have coal, ports and hungry workers. They will become the northern forge of the Crown.",
      pre=[["SPC_roads_of_the_crown"]],
      effect=build(23, "industrial_complex", 1, 1) + build(27, "industrial_complex", 1, 1),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("SPC_synthetic_fuel_programme", 1, 3, "GFX_goal_generic_oil_refinery", "Synthetic Fuel Programme",
      "Occitan and Galician fleets can cut us off from foreign oil. Aragon must learn to make its own.",
      pre=[["SPC_the_arsenal_of_saragossa"]],
      effect=build(30, "synthetic_refinery", 1, 1) + tech("SPC_synthetic_fuel_programme", "synth_resources", 0.5, 1),
      filters=["FOCUS_FILTER_INDUSTRY", "FOCUS_FILTER_RESEARCH"])
focus("SPC_mobilise_war_industry", 3, 3, "GFX_goal_generic_construct_mil_factory", "Mobilise the War Industry",
      "Civilian workshops across the Crown will be converted to produce rifles, shells and engines.",
      pre=[["SPC_the_arsenal_of_saragossa"], ["SPC_the_royal_academies"]],
      effect=build(65, "arms_factory", 1, 1) + build(38, "arms_factory", 1, 1) + build(39, "arms_factory", 1, 1),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("SPC_trans_mediterranean_railways", 5, 3, "GFX_goal_generic_construct_infrastructure", "Trans-Mediterranean Railways",
      "Railways from the Pyrenees to the Bosporus will bind the Crown's scattered dominions into one economy.",
      pre=[["SPC_industrialise_the_northern_isles"]],
      effect=build(54, "infrastructure", 1) + build(51, "infrastructure", 1) + build(22, "infrastructure", 1),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("SPC_the_second_academy", 3, 4, "GFX_goal_generic_scientific_exchange", "The Second Academy",
      "A new technical academy in Valencia will train the engineers that modern war demands.",
      pre=[["SPC_mobilise_war_industry"]], effect="add_research_slot = 1\n",
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_industrial_concentration", 1, 5, "GFX_goal_generic_production", "Industrial Concentration",
      "Fewer, larger and more efficient factories will get more out of every worker and every ton of steel. Aragon is no longer an agrarian nation.",
      pre=[["SPC_synthetic_fuel_programme"], ["SPC_the_second_academy"]],
      effect=("remove_ideas = SPC_agrarian_society\nremove_ideas = SPC_agrarian_society_2\n" +
              tech("SPC_industrial_concentration", "industry", 0.5, 2) + build(68, "industrial_complex", 1, 1)),
      filters=["FOCUS_FILTER_RESEARCH", "FOCUS_FILTER_INDUSTRY"])
focus("SPC_electrical_engineering", 5, 5, "GFX_goal_generic_secret_weapon", "Electrical Engineering",
      "Radio, radar and calculating machines will decide the wars to come.",
      pre=[["SPC_the_second_academy"], ["SPC_trans_mediterranean_railways"]],
      effect=tech("SPC_electrical_engineering", "electronics", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_autarky_of_the_crown", 3, 6, "GFX_goal_generic_military_sphere", "Autarky of the Crown",
      "Aragon's industry now stands on its own feet. No blockade will ever starve the Crown again.",
      pre=[["SPC_industrial_concentration"], ["SPC_electrical_engineering"]],
      effect="add_ideas = SPC_autarky_of_the_crown\n", filters=["FOCUS_FILTER_INDUSTRY"])

# ======================= ARMY =======================
focus("SPC_lessons_of_defeat", 10, 0, "GFX_goal_generic_army_doctrines", "Lessons of Defeat",
      "We lost because Occitanian generals out-thought ours. Every battle of the last war will be studied until its lessons are burned into the officer corps.",
      effect="army_experience = 15\n" + tech("SPC_lessons_of_defeat", "land_doctrine", 0.5, 1), ai=15,
      filters=["FOCUS_FILTER_ARMY_XP", "FOCUS_FILTER_RESEARCH"])
focus("SPC_reform_the_general_staff", 9, 1, "GFX_goal_generic_position_armies", "Reform the General Staff",
      "The general staff will be reorganised around modern planning methods, with Pedro Puig at its head.",
      pre=[["SPC_lessons_of_defeat"]], effect="add_ideas = SPC_reformed_general_staff\n",
      filters=["FOCUS_FILTER_ARMY_XP"])
focus("SPC_rifles_de_deu_contracts", 11, 1, "GFX_goal_generic_small_arms", "Rifles de Déu Contracts",
      "The Rifles de Déu works will receive state contracts for a new generation of infantry weapons.",
      pre=[["SPC_lessons_of_defeat"]],
      effect=tech("SPC_rifles_de_deu_contracts", "infantry_weapons", 0.5, 2) +
             "add_equipment_to_stockpile = { type = infantry_equipment amount = 2000 producer = SPC }\n",
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_revive_the_almogavars", 8, 2, "GFX_goal_generic_special_forces", "Revive the Almogàvers",
      "The Almogàvers, light infantry of terrifying reputation, once carried the banners of Aragon from Sicily to Constantinople. Their name will be given to a new elite corps.",
      pre=[["SPC_reform_the_general_staff"]], effect="add_ideas = SPC_almogavars\n",
      filters=["FOCUS_FILTER_ARMY_XP"])
focus("SPC_the_big_guns", 10, 2, "GFX_goal_generic_army_artillery", "The Big Guns of Aragon",
      "Occitanian trenches will be broken by Aragonese steel. Our artillery will be second to none.",
      pre=[["SPC_rifles_de_deu_contracts"]], effect=tech("SPC_the_big_guns", "artillery", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_motorise_the_legions", 12, 2, "GFX_goal_generic_army_motorized", "Motorise the Legions",
      "Foot and mule will no longer set the pace of our armies.",
      pre=[["SPC_rifles_de_deu_contracts"]], effect=tech("SPC_motorise_the_legions", "motorized_equipment", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_the_pyrenean_mountaineers", 8, 3, "GFX_goal_generic_cavalry", "The Pyrenean Mountaineers",
      "Any war with Occitania will begin in the mountains. Aragon will field the finest mountain troops in Europe.",
      pre=[["SPC_revive_the_almogavars"]], effect=tech("SPC_the_pyrenean_mountaineers", "mountaineers_tech", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_a_new_doctrine_of_war", 10, 3, "GFX_focus_generic_combined_arms", "A New Doctrine of War",
      "From the lessons of defeat, our staff officers have forged a doctrine of our own.",
      pre=[["SPC_the_big_guns"]], effect=tech("SPC_a_new_doctrine_of_war", "land_doctrine", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_armoured_columns", 12, 3, "GFX_goal_generic_army_tanks", "Armoured Columns",
      "Tanks will lead the march to Corsica and beyond.",
      pre=[["SPC_motorise_the_legions"]], effect=tech("SPC_armoured_columns", "armor", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_the_officer_academy", 9, 4, "GFX_goal_generic_army_doctrines", "The Officer Academy of Saragossa",
      "A new military academy will produce officers worthy of the Crown's ambitions.",
      pre=[["SPC_the_pyrenean_mountaineers"], ["SPC_a_new_doctrine_of_war"]],
      effect="add_ideas = SPC_officer_academy\n", filters=["FOCUS_FILTER_ARMY_XP"])
focus("SPC_support_the_line", 11, 4, "GFX_goal_generic_army_artillery2", "Support the Line",
      "Engineers, signals and logistics companies win wars as surely as riflemen.",
      pre=[["SPC_a_new_doctrine_of_war"], ["SPC_armoured_columns"]],
      effect=tech("SPC_support_the_line", "support_tech", 0.5, 2), filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_the_legions_of_the_crown", 10, 5, "GFX_goal_generic_build_tank", "The Legions of the Crown",
      "The army of Aragon is reborn: better led, better armed and burning to avenge its fallen.",
      pre=[["SPC_the_officer_academy"], ["SPC_support_the_line"]],
      effect="add_ideas = SPC_legions_of_the_crown\n", filters=["FOCUS_FILTER_ARMY_XP"])

# ======================= NAVY =======================
focus("SPC_mare_nostrum", 15, 0, "GFX_goal_generic_build_navy", "Mare Nostrum Aragonensis",
      "From Valencia to Smyrna, the Middle Sea is the highway of the Crown. Without command of it our empire falls apart.",
      effect="navy_experience = 15\n" + build(39, "dockyard", 1, 1), ai=10,
      filters=["FOCUS_FILTER_NAVY_XP", "FOCUS_FILTER_INDUSTRY"])
focus("SPC_the_shipyards_of_barcelona", 14, 1, "GFX_goal_generic_construct_naval_dockyard", "The Shipyards of Barcelona",
      "The Drassanes of Barcelona built the galleys of Jaume I. Modern slipways will build the fleet of his heirs.",
      pre=[["SPC_mare_nostrum"]], effect=build(68, "dockyard", 2, 2), filters=["FOCUS_FILTER_INDUSTRY"])
focus("SPC_the_admiralty_reforms", 16, 1, "GFX_goal_generic_navy_doctrines_tactics", "The Admiralty Reforms",
      "Our admirals still think in terms of the last war. That must change.",
      pre=[["SPC_mare_nostrum"]], effect=tech("SPC_the_admiralty_reforms", "naval_doctrine", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_wolves_of_the_middle_sea", 14, 2, "GFX_goal_generic_navy_submarine", "Wolves of the Middle Sea",
      "Submarines will strangle the convoys that feed Occitania's war machine.",
      pre=[["SPC_the_shipyards_of_barcelona"]], effect=tech("SPC_wolves_of_the_middle_sea", "ss_tech", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_cruiser_squadrons", 16, 2, "GFX_goal_generic_navy_cruiser", "Cruiser Squadrons",
      "Fast cruiser squadrons will patrol the long sea lanes between our dominions.",
      pre=[["SPC_the_admiralty_reforms"]],
      effect=tech("SPC_cruiser_squadrons", "ca_tech", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_garrison_the_islands", 14, 3, "GFX_goal_generic_amphibious_assault", "Garrison the Islands",
      "Sicily, Sardinia, Malta and the Balearics are the stepping stones of the Crown. They will be fortified and defended by marines.",
      pre=[["SPC_wolves_of_the_middle_sea"]],
      effect=(bunker(39, "coastal_bunker", 1, "limit_to_coastal") + bunker(41, "coastal_bunker", 1, "limit_to_coastal") +
              bunker(40, "coastal_bunker", 1, "limit_to_coastal") + tech("SPC_garrison_the_islands", "marine_tech", 0.5, 1)),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_a_fleet_worthy_of_the_crown", 15, 4, "GFX_goal_generic_navy_battleship", "A Fleet Worthy of the Crown",
      "Battleships and carriers will show the world that Aragon is once more a great power at sea.",
      pre=[["SPC_garrison_the_islands"], ["SPC_cruiser_squadrons"]],
      effect=tech("SPC_a_fleet_worthy_of_the_crown", "bb_tech", 0.5, 1) + tech("SPC_a_fleet_worthy_of_the_crown_cv", "cv_tech", 0.5, 1) +
             "navy_experience = 25\n",
      filters=["FOCUS_FILTER_RESEARCH", "FOCUS_FILTER_NAVY_XP"])

# ======================= AIR =======================
focus("SPC_the_aragonese_air_corps", 19, 0, "GFX_goal_generic_build_airforce", "The Aragonese Air Corps",
      "The last war showed that whoever rules the skies rules the battlefield. Aragon will build an independent air corps.",
      effect="air_experience = 15\n" + build(30, "air_base", 2), ai=10, filters=["FOCUS_FILTER_AIR_XP"])
focus("SPC_falcons_of_the_pyrenees", 18, 1, "GFX_goal_generic_air_fighter", "Falcons of the Pyrenees",
      "Fighter squadrons will guard the skies over the mountains.",
      pre=[["SPC_the_aragonese_air_corps"]], effect=tech("SPC_falcons_of_the_pyrenees", "light_fighter", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_doctrine_of_the_skies", 20, 1, "GFX_goal_generic_air_doctrine", "Doctrine of the Skies",
      "Our airmen need a doctrine of their own, not one borrowed from the army.",
      pre=[["SPC_the_aragonese_air_corps"]], effect=tech("SPC_doctrine_of_the_skies", "air_doctrine", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_close_support_wings", 18, 2, "GFX_goal_generic_CAS", "Close Support Wings",
      "Dive bombers will clear the way through the Pyrenean passes.",
      pre=[["SPC_falcons_of_the_pyrenees"]], effect=tech("SPC_close_support_wings", "cas_bomber", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_strike_over_the_middle_sea", 20, 2, "GFX_goal_generic_air_naval_bomber", "Strike Over the Middle Sea",
      "Land-based torpedo bombers can make the Middle Sea a graveyard for enemy fleets.",
      pre=[["SPC_doctrine_of_the_skies"]], effect=tech("SPC_strike_over_the_middle_sea", "naval_bomber", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_bombers_of_the_crown", 19, 3, "GFX_goal_generic_air_bomber", "Bombers of the Crown",
      "Medium bombers will carry the war to Occitanian cities and factories.",
      pre=[["SPC_close_support_wings", "SPC_strike_over_the_middle_sea"]],
      effect=tech("SPC_bombers_of_the_crown", "tactical_bomber", 0.5, 2), filters=["FOCUS_FILTER_RESEARCH"])
focus("SPC_the_aircraft_works", 19, 4, "GFX_goal_generic_air_fighter2", "The Aircraft Works",
      "The Bombarders Bascos works will be expanded into the largest aircraft plant in the Middle Sea.",
      pre=[["SPC_bombers_of_the_crown"]], effect=build(30, "arms_factory", 1, 1) + "air_experience = 25\n",
      filters=["FOCUS_FILTER_INDUSTRY", "FOCUS_FILTER_AIR_XP"])


# ---------- emit focus tree ----------
def indent(text, n):
    pad = "\t" * n
    return "".join(pad + l + "\n" if l.strip() else "\n" for l in text.strip("\n").split("\n"))

out = []
out.append("focus_tree = {\n\tid = SPC_focus\n\n\tcountry = {\n\t\tfactor = 0\n\t\tmodifier = {\n\t\t\tadd = 10\n\t\t\toriginal_tag = SPC\n\t\t}\n\t}\n\n\tdefault = no\n\n\tinitial_show_position = { focus = SPC_the_bitter_peace }\n\n")
for f in F:
    s = "\tfocus = {\n"
    s += f"\t\tid = {f['id']}\n\t\ticon = {f['icon']}\n\t\tx = {f['x']}\n\t\ty = {f['y']}\n\t\tcost = {f['cost']}\n"
    for group in f["pre"]:
        s += "\t\tprerequisite = { " + " ".join(f"focus = {p}" for p in group) + " }\n"
    if f["excl"]:
        s += "\t\tmutually_exclusive = { " + " ".join(f"focus = {p}" for p in f["excl"]) + " }\n"
    if f["avail"]:
        s += "\t\tavailable = {\n" + indent(f["avail"], 3) + "\t\t}\n"
    if f["bypass"]:
        s += "\t\tbypass = {\n" + indent(f["bypass"], 3) + "\t\t}\n"
    if f["filters"]:
        s += "\t\tsearch_filters = { " + " ".join(f["filters"]) + " }\n"
    s += "\t\tcompletion_reward = {\n" + indent(f["effect"], 3) + "\t\t}\n"
    s += f"\t\tai_will_do = {{ factor = {f['ai']} }}\n"
    s += "\t}\n\n"
    out.append(s)
out.append("}\n")
open(os.path.join(REPO, "common/national_focus/SPC_NF.txt"), "w", encoding="utf-8", newline="\n").write("".join(out))

# ---------- ideas ----------
IDEAS = [
    ("SPC_agrarian_society", "generic_agrarian_society", "industrial_capacity_factory = -0.15\nproduction_speed_buildings_factor = -0.15\nresearch_speed_factor = -0.05",
     "Agrarian Society", "Aragon's wealth has always come from land and empire, not industry. Most Aragonese still work the fields, and the few factories cannot match those of Occitania."),
    ("SPC_agrarian_society_2", "generic_agrarian_society", "industrial_capacity_factory = -0.05\nproduction_speed_buildings_factor = -0.05",
     "Industrialising Society", "Workers are leaving the countryside for the new factories of Valencia and Naples, but Aragon is still catching up."),
    ("SPC_triple_monarchy", "SPC_monarch", "stability_factor = 0.1\npolitical_power_gain = 0.1\nwar_support_factor = 0.05",
     "The Triple Monarchy", "Aragon, France and England are united under one crown, as they were under Guillen IV."),
    ("SPC_emperor_of_three_crowns", "warrior_traditions_idea", "war_support_factor = 0.1\narmy_attack_factor = 0.05\nindustrial_capacity_factory = 0.05",
     "Emperor of Three Crowns", "The emperor commands the armies and workshops of three kingdoms."),
    ("SPC_imperial_eagle", "SPC_monarch", "war_support_factor = 0.1\npolitical_power_gain = 0.05\nstability_factor = 0.05",
     "The Imperial Eagle", "A Bonaparte sits on the throne of Aragon again, and the nation remembers the days when it ruled Europe."),
    ("SPC_pincer_plan", "generic_infantry_bonus", "max_planning = 0.1\nwar_support_factor = 0.05",
     "The Pincer Plan", "Aragon and Scandinavia have agreed a joint plan to strike Occitania from north and south at once."),
    ("SPC_heirs_of_alexander", "generic_morale_bonus", "war_support_factor = 0.05\nexperience_gain_army_factor = 0.05\nstability_factor = -0.05",
     "Heirs of Alexander", "Aragon has revived the dream of conquering the Orient. Many remember what it cost last time."),
    ("SPC_alexanders_legacy", "warrior_traditions_idea", "war_support_factor = 0.1\narmy_attack_factor = 0.05\nstability_factor = 0.05",
     "Alexander's Legacy", "Where twenty kings failed, this generation has succeeded. The Orient bows to Aragon."),
    ("SPC_europe_first", "generic_pp_unity_bonus", "stability_factor = 0.05\nproduction_speed_buildings_factor = 0.05",
     "Europe First", "Aragon has turned its back on the Oriental dream to focus on its European heartland."),
    ("SPC_eyes_on_the_pyrenees", "generic_national_unification", "stability_factor = 0.05\nproduction_speed_buildings_factor = 0.05\narmy_core_attack_factor = 0.1",
     "Eyes on the Pyrenees", "Every resource of the Crown is devoted to retaking the lost provinces."),
    ("SPC_wounds_of_defeat", "generic_army_problems", "stability_factor = -0.1\npolitical_power_gain = -0.1\nwar_support_factor = -0.05",
     "The Wounds of Defeat", "From Napoleon's fall to the last war with Occitania, Aragon has lost every war it fought for a century. The nation is bitter, divided and exhausted, and it knows it survived only because foreign powers intervened. Until it finds a new direction, this wound will not heal."),
    ("SPC_revanchist_fervor", "generic_fascism_drift_bonus", "war_support_factor = 0.1\nfascism_drift = 0.05\nconscription = 0.01",
     "Revanchist Fervour", "Shame has become rage, and rage has become purpose. Aragon lives for the day of reckoning."),
    ("SPC_saragossa_militia", "generic_recruit_centers", "stability_factor = 0.05\nconscription = 0.005\ndrift_defence_factor = 0.15",
     "The Saragossa Militia", "The Moviment's black shirts patrol every town square, keeping order and watching for traitors."),
    ("SPC_corporate_state", "generic_production_bonus", "production_speed_buildings_factor = 0.1\nindustrial_capacity_factory = 0.05\nstability_factor = -0.02",
     "The Corporate State", "State syndicates direct the economy. Strikes are illegal, and every factory serves the nation."),
    ("SPC_aragon_above_all", "generic_morale_bonus", "war_support_factor = 0.1\narmy_core_attack_factor = 0.1\narmy_core_defence_factor = 0.1",
     "Aragon Above All", "The nation stands united behind the Cabdill and the cause of revanche."),
    ("SPC_crown_of_aragon", "SPC_monarch", "stability_factor = 0.1\npolitical_power_gain = 0.1",
     "The Crown of Aragon", "King Jaume V has restored the ancient Crown. For many Aragonese, the throne is the one institution untouched by the shame of defeat."),
    ("SPC_royal_council", "generic_pp_unity_bonus", "political_power_gain = 0.15\ndrift_defence_factor = 0.25",
     "The Royal Council", "Nobles, bishops and marshals advise the king and keep the dangerous ideas of the street at bay."),
    ("SPC_second_conqueror", "warrior_traditions_idea", "army_attack_factor = 0.05\nwar_support_factor = 0.1\nexperience_gain_army_factor = 0.1",
     "The Second Conqueror", "King Jaume V rides at the head of his armies, as his namesake did seven centuries ago."),
    ("SPC_free_corts", "generic_democratic_drift_bonus", "stability_factor = 0.05\npolitical_power_gain = 0.1\ndemocratic_drift = 0.05",
     "The Free Corts", "Aragon's parliament sits again, and its debates are reported freely in every newspaper."),
    ("SPC_collective_security", "generic_national_unification", "war_support_factor = 0.1\njustify_war_goal_time = -0.25",
     "Collective Security", "Aragon and its partners have pledged to answer Occitan aggression together."),
    ("SPC_plan_of_restoration", "generic_production_bonus", "production_speed_buildings_factor = 0.1",
     "The Plan of Restoration", "A national plan directs investment into rebuilding Aragon's shattered industry."),
    ("SPC_autarky_of_the_crown", "generic_military_industry", "industrial_capacity_factory = 0.1\nproduction_factory_max_efficiency_factor = 0.05",
     "Autarky of the Crown", "Aragonese industry is self-sufficient and geared for a long war."),
    ("SPC_reformed_general_staff", "generic_infantry_bonus", "planning_speed = 0.1\nmax_planning = 0.05",
     "Reformed General Staff", "A modern general staff plans the Crown's campaigns down to the last railway timetable."),
    ("SPC_almogavars", "generic_war_of_national_liberation", "special_forces_cap = 0.1\nspecial_forces_attack_factor = 0.1",
     "The Almogàvers", "Aragon's elite light infantry carry the name and the reputation of the medieval Almogàvers."),
    ("SPC_officer_academy", "generic_artillery_regiments", "army_org_factor = 0.05\narmy_leader_start_level = 1",
     "The Officer Academy of Saragossa", "Aragon's new officers are trained in the lessons of the last war."),
    ("SPC_legions_of_the_crown", "generic_manpower_bonus", "army_attack_factor = 0.05\narmy_defence_factor = 0.05",
     "The Legions of the Crown", "A reborn army, better led and better armed, eager to avenge its fallen."),
]
s = "ideas = {\n\tcountry = {\n"
for key, pic, mod, _, _ in IDEAS:
    removal = "\t\t\tremoval_cost = -1\n"
    s += f"\t\t{key} = {{\n\t\t\tpicture = {pic}\n\t\t\tallowed = {{ original_tag = SPC }}\n{removal}\t\t\tmodifier = {{\n" + indent(mod, 4) + "\t\t\t}\n\t\t}\n"
s += "\t}\n}\n"
open(os.path.join(REPO, "common/ideas/SPC_focus_ideas.txt"), "w", encoding="utf-8", newline="\n").write(s)

# ---------- localisation ----------
def q(t):
    return t.replace('"', '\\"')
L = ["l_english:"]
L.append(" # Aragon focus tree")
for f in F:
    L.append(f' {f["id"]}:0 "{q(f["name"])}"')
    L.append(f' {f["id"]}_desc:0 "{q(f["desc"])}"')
L.append(" SPC_a_fleet_worthy_of_the_crown_cv:0 \"A Fleet Worthy of the Crown\"")
L.append(" # Ideas")
for key, _, _, name, desc in IDEAS:
    L.append(f' {key}:0 "{q(name)}"')
    L.append(f' {key}_desc:0 "{q(desc)}"')
L.append(" # Factions, threats, characters")
L.append(' SPC_pact_of_saragossa:0 "Pact of Saragossa"')
L.append(' SPC_alliance_of_crowns:0 "Alliance of Crowns"')
L.append(' SPC_middle_sea_entente:0 "Middle Sea Entente"')
L.append(' SPC_revanche_threat:0 "Aragonese War of Revanche"')
L.append(' SPC_jaume_v:0 "Jaume V"')
L.append(' SPC_josep_ferrer:0 "Josep Ferrer i Bosch"')
L.append(' SPC_napoleo_iv:0 "Napoleó IV Bonaparte"')
L.append(' SPC_northern_pact:0 "Northern Pact"')
L.append(' SPC_triple_monarchy:0 "Triple Monarchy"')
L.append(' SPC_triple_monarchy_ADJ:0 "Imperial"')
L.append(' SPC_triple_monarchy_DEF:0 "the Triple Monarchy"')
L.append(' SPC_unlock_triple_monarchy_tt:0 "Unlocks the decision §YRestore the Triple Monarchy§!."')
L.append(' SPC_form_triple_monarchy:0 "Restore the Triple Monarchy"')
L.append(' SPC_form_triple_monarchy_desc:0 "With Paris, London and Saragossa in our hands, the three crowns of Guillen IV can be united again under one emperor."')
L.append(' SPC_bonapartist:0 "Empire of Aragon"')
L.append(' SPC_bonapartist_ADJ:0 "Aragonese"')
L.append(' SPC_bonapartist_DEF:0 "the Empire of Aragon"')
open(os.path.join(REPO, "localisation/english/SPC_focus_l_english.yml"), "w", encoding="utf-8-sig", newline="\n").write("\n".join(L) + "\n")

print(len(F), "focuses")
