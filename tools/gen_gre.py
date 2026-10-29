# Greece (GRE) focus tree, Greek Uprising mechanic, Hellenic Republic (HEL) tag.
import sys, os, re
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
def tech(name, cat, bonus=0.5, uses=1):
    if cat.endswith("_doctrine"):
        return f"add_doctrine_cost_reduction = {{ name = {name} cost_reduction = 0.4 uses = {uses} category = {cat} }}\n"
    return f"add_tech_bonus = {{ name = {name} bonus = {bonus} uses = {uses} category = {cat} }}\n"

ROYAL = [70, 100, 99]     # East Macedonia (Salonika), Thessaly, West Macedonia
REPUB = [49, 62, 50]      # Attica (Athens), Peloponnese, Aegean Islands
GREEK = ROYAL + REPUB

UPRISING = (
    "# Royalist rebels rise in the north and join Greece\n"
    + "".join(f"if = {{ limit = {{ {s} = {{ is_owned_and_controlled_by = SPC }} }} transfer_state = {s} }}\n" for s in ROYAL)
    + "load_oob = \"GRE_uprising\"\n"
    + "if = { limit = { has_country_flag = GRE_royalist_committees SPC = { NOT = { has_country_flag = SPC_hetairists_suppressed } } }\n\tload_oob = \"GRE_uprising_extra\"\n}\n"
    + "add_equipment_to_stockpile = { type = infantry_equipment amount = 2000 producer = GRE }\n"
    + "# Republican rebels rise in the south as the Hellenic Republic\n"
    + "".join(f"{s} = {{ add_core_of = HEL }}\n" for s in REPUB)
    + "SPC = { release = HEL }\n"
    + "HEL = {\n\tload_oob = \"HEL_uprising\"\n"
    + "\tif = { limit = { ROOT = { has_country_flag = GRE_republican_contacts } SPC = { NOT = { has_country_flag = SPC_hetairists_suppressed } } }\n\t\tload_oob = \"HEL_uprising_extra\"\n\t}\n"
    + "\tadd_equipment_to_stockpile = { type = infantry_equipment amount = 2000 producer = HEL }\n\tadd_ideas = GRE_the_great_uprising\n"
    + "}\n"
    + "# Aragon moves to crush both rebel governments\n"
    + "SPC = {\n\tdeclare_war_on = { target = ROOT type = annex_everything }\n"
    + "\tif = { limit = { country_exists = HEL } declare_war_on = { target = HEL type = annex_everything } }\n}\n"
    + "if = { limit = { has_country_flag = GRE_occitan_volunteers }\n\tload_oob = \"GRE_occitan_volunteers\"\n\tadd_equipment_to_stockpile = { type = infantry_equipment amount = 1000 producer = OCC }\n}\n"
    + "# Royalists and republicans are rivals: the uprising is a three-way war\n"
    + "if = { limit = { country_exists = HEL NOT = { has_war_with = HEL } }\n"
    + "\tdeclare_war_on = { target = HEL type = annex_everything }\n"
    + "\tadd_opinion_modifier = { target = HEL modifier = negative_50 }\n"
    + "\tHEL = { add_opinion_modifier = { target = ROOT modifier = negative_50 } }\n}\n"
    + "if = { limit = { has_country_flag = GRE_monastery_presses } SPC = { add_stability = -0.05 } }\n"
    + "SPC = { country_event = { id = greek_uprising.1 } }\n"
    + "add_ideas = GRE_the_great_uprising\n"
)

# ---------------- uprising core ----------------
focus("GRE_the_last_free_greeks", 8, 0, "GFX_goal_generic_national_unity", "The Last Free Greeks",
      "Polygyros is all that remains of free Greece. Athens, Salonika and the islands groan under Aragonese rule. But every Greek in the occupied lands still looks north to the last Hellenic flag.",
      cost=5, effect="add_political_power = 75\nadd_stability = 0.05\n", ai=50, filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_the_philiki_etaireia_reborn", 8, 1, "GFX_goal_generic_political_pressure", "The Philiki Etaireia Reborn",
      "A century ago the Friendly Society plotted the liberation of Greece from the Turks. Its heirs now plot liberation from Aragon, in cellars from Salonika to Nafplio.",
      pre=[["GRE_the_last_free_greeks"]],
      effect="".join(f"add_state_claim = {s}\n" for s in GREEK) + "add_war_support = 0.1\n",
      ai=20, filters=["FOCUS_FILTER_ANNEXATION", "FOCUS_FILTER_WAR_SUPPORT"])
focus("GRE_royalist_committees", 6, 2, "GFX_focus_hun_elect_a_king", "Royalist Committees in Salonika",
      "In Macedonia and Thessaly the old families remain loyal to the Greek crown. When the signal comes, their committees will raise the north for the king.",
      pre=[["GRE_the_philiki_etaireia_reborn"]],
      effect="set_country_flag = GRE_royalist_committees\nadd_popularity = { ideology = absolutist popularity = 0.05 }\n",
      ai=10, filters=["FOCUS_FILTER_MANPOWER"])
focus("GRE_smuggle_arms_across_the_aegean", 8, 2, "GFX_goal_generic_small_arms", "Smuggle Arms Across the Aegean",
      "Fishing boats by day, gun-runners by night. Every rifle that reaches the occupied lands is one more Aragonese garrison that will not sleep soundly.",
      pre=[["GRE_the_philiki_etaireia_reborn"]],
      effect="add_equipment_to_stockpile = { type = infantry_equipment amount = 1500 producer = GRE }\nadd_equipment_to_stockpile = { type = artillery_equipment amount = 36 producer = GRE }\n",
      ai=20, filters=["FOCUS_FILTER_MANPOWER"])
focus("GRE_the_athenian_republicans", 10, 2, "GFX_goal_support_democracy", "Reach Out to the Athenian Republicans",
      "The rebels of Athens and the Peloponnese want no king. They want a Hellenic Republic, and when the uprising comes they will fight us as readily as Aragon. Still, keeping a line open to Athens will put more guns in the south, and one day there may be a peace to make.",
      pre=[["GRE_the_philiki_etaireia_reborn"]],
      effect="set_country_flag = GRE_republican_contacts\nadd_popularity = { ideology = democratic popularity = 0.05 }\n",
      ai=5, filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_the_great_uprising", 8, 3, "GFX_goal_generic_major_war", "The Great Uprising",
      "The signal fires burn on Mount Olympus. Salonika, Volos and Florina rise for the king, while Athens and the islands proclaim a Hellenic Republic that recognises no king. Three armies now fight over Greece.",
      pre=[["GRE_smuggle_arms_across_the_aegean"], ["GRE_royalist_committees", "GRE_the_athenian_republicans"]],
      avail=("country_exists = SPC\nNOT = { has_war_with = SPC }\n"
             "OR = {\n" + "".join(f"\t{s} = {{ is_owned_by = SPC }}\n" for s in GREEK) + "}\n"
             "OR = { date > 1937.1.1 SPC = { has_war = yes } }"),
      effect=UPRISING, ai=50, filters=["FOCUS_FILTER_ANNEXATION"])

# ---------------- who leads Greece ----------------
focus("GRE_a_crown_for_all_hellenes", 6, 4, "GFX_focus_rom_royal_dictatorship", "A Crown for All Hellenes",
      "The royalists of the north fought for the king. Greece will be liberated as a kingdom, and the republican experiment in Athens is a dangerous distraction.",
      pre=[["GRE_the_great_uprising"]], excl=["GRE_the_republican_pact"],
      effect="add_popularity = { ideology = absolutist popularity = 0.1 }\nadd_stability = 0.05\n",
      ai=5, filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_bring_athens_to_heel", 5, 5, "GFX_goal_generic_territory_or_war", "Bring Athens to Heel",
      "The war with Aragon is over. Every soldier of the crown now marches on Athens, and the self-proclaimed republic will submit.",
      pre=[["GRE_a_crown_for_all_hellenes"]],
      avail="country_exists = HEL\nNOT = { has_war_with = SPC }",
      effect=("if = { limit = { has_war_with = HEL }\n\tadd_timed_idea = { idea = GRE_march_on_athens days = 180 }\n\tadd_war_support = 0.1\n}\n"
              "else = { create_wargoal = { type = annex_everything target = HEL } }\n"),
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("GRE_the_king_in_athens", 7, 5, "GFX_goal_generic_national_unity", "The King in Athens",
      "Athens is the heart of Hellas. The court will move from little Polygyros to the city of Pericles.",
      pre=[["GRE_a_crown_for_all_hellenes"]], avail="owns_state = 49",
      effect="set_capital = { state = 49 }\nadd_stability = 0.1\nadd_political_power = 100\n", filters=["FOCUS_FILTER_STABILITY"])
focus("GRE_the_republican_pact", 10, 4, "GFX_goal_support_democracy", "The Republican Pact",
      "Greeks killing Greeks while Aragon watches is madness. The king will step aside, the guns will fall silent between Polygyros and Athens, and Greece will join the Hellenic Republic as one free nation.",
      pre=[["GRE_the_great_uprising"]], excl=["GRE_a_crown_for_all_hellenes"],
      effect=("if = { limit = { country_exists = HEL has_war_with = HEL }\n\twhite_peace = HEL\n}\n"
              "if = { limit = { country_exists = HEL }\n"
              "\tadd_opinion_modifier = { target = HEL modifier = positive_50 }\n"
              "\tHEL = { add_opinion_modifier = { target = ROOT modifier = positive_50 } }\n}\n"
              "set_politics = { ruling_party = democratic elections_allowed = yes last_election = \"1936.1.1\" election_frequency = 48 }\n"
              "set_popularities = { democratic = 60 absolutist = 35 fascism = 5 }\n"
              "if = { limit = { country_exists = HEL is_in_faction = no HEL = { is_in_faction = no } }\n"
              "\tcreate_faction_from_template = { template = faction_template_defensive_democratic name = GRE_hellenic_alliance }\n"
              "\tadd_to_faction = HEL\n}\n"),
      ai=2, filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_union_with_the_republic", 9, 5, "GFX_focus_generic_treaty", "Union with the Hellenic Republic",
      "With Aragon beaten back, the two Greek states will become one. The Hellenic Republic and the old kingdom unite under a single constitution in Athens.",
      pre=[["GRE_the_republican_pact"]],
      avail="country_exists = HEL\nHEL = { is_in_faction_with = ROOT }\nNOT = { has_war_with = SPC }",
      effect="annex_country = { target = HEL transfer_troops = yes }\nadd_stability = 0.1\n",
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("GRE_a_constitution_for_hellas", 11, 5, "GFX_focus_generic_treaty", "A Constitution for Hellas",
      "A written constitution, a free parliament and an end to the arbitrary rule of kings and foreign governors.",
      pre=[["GRE_the_republican_pact"]],
      effect="add_ideas = GRE_hellenic_constitution\n", filters=["FOCUS_FILTER_STABILITY"])
focus("GRE_hellas_reborn", 8, 6, "GFX_goal_generic_national_unity", "Hellas Reborn",
      "From Salonika to Sparta, Greece is free and united for the first time in living memory.",
      pre=[["GRE_bring_athens_to_heel", "GRE_the_king_in_athens", "GRE_union_with_the_republic", "GRE_a_constitution_for_hellas"]],
      avail="owns_state = 49\nowns_state = 70",
      effect="".join(f"add_state_core = {s}\n" for s in GREEK) + "add_ideas = GRE_hellas_reborn\n",
      filters=["FOCUS_FILTER_ANNEXATION", "FOCUS_FILTER_STABILITY"])
focus("GRE_the_megali_idea", 8, 7, "GFX_goal_generic_more_territorial_claims", "The Megali Idea",
      "The Great Idea: a Greek state embracing every Greek, with Constantinople as its capital. The City is held by Aragon, and Smyrna too. Not for long.",
      pre=[["GRE_hellas_reborn"]], avail="country_exists = SPC",
      effect=("add_state_claim = 52\nadd_state_claim = 54\nadd_state_claim = 753\n"
              "create_wargoal = { type = take_state_focus target = SPC generator = { 52 54 } }\n"),
      filters=["FOCUS_FILTER_ANNEXATION"])

# ---------------- foreign friends ----------------
focus("GRE_appeal_to_occitania", 13, 1, "GFX_focus_generic_treaty", "Appeal to Occitania",
      "The enemy of our enemy is the strongest power in Europe. Occitania has no love for Greeks, but it will gladly arm anyone who bleeds Aragon.",
      pre=[["GRE_the_last_free_greeks"]], avail="country_exists = OCC",
      effect=("add_opinion_modifier = { target = OCC modifier = positive_50 }\n"
              "OCC = { add_opinion_modifier = { target = ROOT modifier = positive_50 } }\n"
              "add_equipment_to_stockpile = { type = infantry_equipment amount = 1000 producer = OCC }\n"),
      filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_occitan_military_advisors", 13, 2, "GFX_goal_generic_army_doctrines", "Occitan Military Advisors",
      "Officers from the army that beat Aragon again and again will teach our guerrillas how it is done.",
      pre=[["GRE_appeal_to_occitania"]],
      effect="army_experience = 15\n" + tech("GRE_occitan_military_advisors", "land_doctrine", 0.5, 1),
      filters=["FOCUS_FILTER_ARMY_XP"])
focus("GRE_the_occitan_volunteer_corps", 12, 3, "GFX_goal_generic_allies_build_infantry", "The Occitan Volunteer Corps",
      "Occitania will not go to war for Greece. But nobody in Toulouse will stop veterans of the Aragonese wars from taking leave, crossing the Adriatic and fighting under a Greek flag.",
      pre=[["GRE_occitan_military_advisors"]], avail="country_exists = OCC\nOCC = { NOT = { has_war_with = ROOT } }",
      effect=("set_country_flag = GRE_occitan_volunteers\n"
              "if = { limit = { has_completed_focus = GRE_the_great_uprising has_war_with = SPC }\n"
              "\tload_oob = \"GRE_occitan_volunteers\"\n\tadd_equipment_to_stockpile = { type = infantry_equipment amount = 1000 producer = OCC }\n}\n"),
      filters=["FOCUS_FILTER_MANPOWER"])
focus("GRE_byzantine_brotherhood", 14, 3, "GFX_focus_generic_treaty", "Byzantine Brotherhood",
      "The Byzantine Empire also lost Thessaly and Macedonia to Aragon. Orthodox brothers should not fight each other while the Catalans rule our lands.",
      pre=[["GRE_appeal_to_occitania"]], avail="country_exists = X09\nNOT = { has_war_with = X09 }",
      effect=("add_opinion_modifier = { target = X09 modifier = positive_50 }\n"
              "X09 = { add_opinion_modifier = { target = ROOT modifier = positive_50 } }\n"
              "diplomatic_relation = { country = X09 relation = non_aggression_pact }\n"),
      filters=["FOCUS_FILTER_POLITICAL"])

# ---------------- army and economy ----------------
focus("GRE_the_klephts", 2, 1, "GFX_goal_generic_special_forces", "The Klephts",
      "The mountain bandits who fought the Turks for four centuries live on in every Greek village. Their tactics will be the backbone of our army.",
      pre=[["GRE_the_last_free_greeks"]], effect="add_ideas = GRE_klephts\nrecruit_character = GRE_giorgos_zachos\n", filters=["FOCUS_FILTER_ARMY_XP"])
focus("GRE_the_evzones", 1, 2, "GFX_goal_generic_allies_build_infantry", "The Evzones",
      "The kilted mountain infantry of the old royal guard will be revived as the elite of the liberation army.",
      pre=[["GRE_the_klephts"]], effect="army_experience = 15\n" + tech("GRE_the_evzones", "infantry_weapons", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH", "FOCUS_FILTER_ARMY_XP"])
focus("GRE_mountain_warfare", 3, 2, "GFX_goal_generic_cavalry", "Mountain Warfare",
      "Pindus and Olympus are our fortresses. Our soldiers will learn to fight in them.",
      pre=[["GRE_the_klephts"]], effect=tech("GRE_mountain_warfare", "mountaineers_tech", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("GRE_the_diaspora_volunteers", 2, 3, "GFX_goal_generic_allies_build_infantry", "Volunteers from the Diaspora",
      "Greeks from Alexandria to Odessa answer the call of the motherland.",
      pre=[["GRE_the_evzones"], ["GRE_mountain_warfare"]], effect="add_manpower = 15000\n",
      filters=["FOCUS_FILTER_MANPOWER"])
focus("GRE_rebuild_polygyros", 0, 1, "GFX_goal_generic_construct_civ_factory", "Rebuild Polygyros",
      "Our only province must also be our workshop.",
      pre=[["GRE_the_last_free_greeks"]], effect=build(329, "industrial_complex", 1, 1) + build(329, "infrastructure", 1),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("GRE_aegean_fishing_fleets", 0, 2, "GFX_goal_generic_construct_naval_dockyard", "Aegean Fishing Fleets",
      "The fishing boats of Chalkidiki will become the core of a Greek navy, and of our smuggling routes.",
      pre=[["GRE_rebuild_polygyros"]], effect=build(329, "dockyard", 1, 1) + "navy_experience = 10\n",
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("GRE_industry_of_a_free_greece", 2, 5, "GFX_goal_generic_construct_mil_factory", "Industry of a Free Greece",
      "The workshops of Athens and Salonika will now arm Greeks instead of Aragonese.",
      pre=[["GRE_the_great_uprising"], ["GRE_the_diaspora_volunteers"]],
      effect=build(70, "industrial_complex", 1, 1) + build(70, "arms_factory", 1, 1) + build(49, "arms_factory", 1, 1),
      filters=["FOCUS_FILTER_INDUSTRY"])

# ================= EXPANSION (Oct 2026): court, church, society, economy, army, regimes =================
def bunker(state, btype, level, sel):
    return (f"if = {{ limit = {{ {state} = {{ is_owned_and_controlled_by = ROOT }} }}\n"
            f"\t{state} = {{ add_building_construction = {{ type = {btype} level = {level} "
            f"province = {{ all_provinces = yes {sel} = yes }} instant_build = yes }} }}\n}}\n")
def leader(char):
    return f"recruit_character = {char}\npromote_character = {char}\n"

# ---------------- the court in Polygyros and the Holy Mountain (before the uprising) ----------------
focus("GRE_the_court_at_polygyros", 17, 1, "GFX_focus_hun_elect_a_king", "The Court at Polygyros",
      "King Andreas Kolokotronis keeps a court of exiles in a provincial town hall: old generals, deposed mayors and the great-grandsons of the heroes of 1821. It is a small court, but it is the only Greek one left.",
      pre=[["GRE_the_last_free_greeks"]], effect="add_political_power = 50\nadd_stability = 0.05\n",
      ai=10, filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_the_holy_mountain", 16, 2, "GFX_goal_generic_national_unity", "The Holy Mountain",
      "On Mount Athos, at the tip of our own peninsula, twenty monasteries have prayed for Greece for a thousand years. The abbots have sent word: the Holy Mountain stands with the king.",
      pre=[["GRE_the_court_at_polygyros"]], effect="add_ideas = GRE_blessing_of_athos\n",
      filters=["FOCUS_FILTER_STABILITY"])
focus("GRE_the_monastery_presses", 16, 3, "GFX_goal_generic_propaganda", "The Monastery Presses",
      "The old printing presses of Athos once printed psalters. Now they print pamphlets, carried by pilgrims and mule drivers into every village Aragon holds.",
      pre=[["GRE_the_holy_mountain"]],
      effect="set_country_flag = GRE_monastery_presses\nadd_war_support = 0.05\n",
      filters=["FOCUS_FILTER_WAR_SUPPORT"])
focus("GRE_refugees_of_macedonia", 18, 2, "GFX_goal_generic_allies_build_infantry", "Refugees of Macedonia",
      "Thousands of Greeks have fled Aragonese Macedonia into Chalkidiki. They sleep in churches and olive groves, and every one of them wants to go home with a rifle.",
      pre=[["GRE_the_court_at_polygyros"]], effect="add_manpower = 8000\n" + build(329, "infrastructure", 1),
      filters=["FOCUS_FILTER_MANPOWER"])
focus("GRE_the_crown_prince", 18, 3, "GFX_goal_generic_army_doctrines", "The Crown Prince Takes Command",
      "Crown Prince Konstantinos is young, impatient and adored by the refugee volunteers. His father has finally agreed to let him command.",
      pre=[["GRE_refugees_of_macedonia"]], effect="recruit_character = GRE_konstantinos_kolokotronis\narmy_experience = 5\n",
      filters=["FOCUS_FILTER_ARMY_XP"])
focus("GRE_the_sacred_band", 17, 4, "GFX_goal_generic_special_forces", "The Sacred Band",
      "Three hundred volunteers swear an oath before the relics of Athos to die rather than retreat, as the Sacred Band of Ypsilantis did in 1821.",
      pre=[["GRE_the_monastery_presses"], ["GRE_the_crown_prince"]],
      effect="load_oob = \"GRE_sacred_band\"\n" + tech("GRE_the_sacred_band", "special_forces", 0.5, 1),
      filters=["FOCUS_FILTER_MANPOWER", "FOCUS_FILTER_RESEARCH"])

# ---------------- a free Greek society (after the uprising) ----------------
focus("GRE_return_of_the_refugees", 18, 5, "GFX_goal_generic_construct_infrastructure", "Return of the Refugees",
      "Salonika is Greek again, and the refugee camps of Chalkidiki empty in a week. The roads north are full of carts, icons and children.",
      pre=[["GRE_the_great_uprising"], ["GRE_refugees_of_macedonia"]], avail="owns_state = 70",
      effect="add_stability = 0.05\nadd_manpower = 5000\n" + build(70, "infrastructure", 1),
      filters=["FOCUS_FILTER_STABILITY", "FOCUS_FILTER_MANPOWER"])
focus("GRE_rebuild_the_burned_villages", 19, 6, "GFX_goal_generic_construct_civ_factory", "Rebuild the Burned Villages",
      "Aragonese reprisals left a line of ashes from Florina to Volos. Every rebuilt church and schoolhouse is a promise that it will not happen again.",
      pre=[["GRE_return_of_the_refugees"]], effect="add_stability = 0.05\n" + build(99, "industrial_complex", 1, 1),
      filters=["FOCUS_FILTER_STABILITY", "FOCUS_FILTER_INDUSTRY"])
focus("GRE_the_language_question", 17, 6, "GFX_goal_generic_scientific_exchange", "The Language Question",
      "Should a free Greece write in Katharevousa, the purified tongue of the courts and the Church, or in Demotiki, the Greek its people actually speak? The quarrel has ended friendships and started riots.",
      pre=[["GRE_the_great_uprising"]], effect="add_political_power = 25\n", filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_katharevousa", 16, 7, "GFX_goal_generic_propaganda", "Katharevousa",
      "The language of Byzantium and the Gospels will be the language of the state. A nation reborn must sound like the nation it once was.",
      pre=[["GRE_the_language_question"]], excl=["GRE_demotiki"],
      effect="add_ideas = GRE_katharevousa\nadd_popularity = { ideology = absolutist popularity = 0.05 }\n",
      ai=3, filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_demotiki", 18, 7, "GFX_goal_support_democracy", "Demotiki",
      "Schoolchildren will learn the Greek their grandmothers speak. Literacy and pride will spread faster than any decree from Athens.",
      pre=[["GRE_the_language_question"]], excl=["GRE_katharevousa"],
      effect="add_ideas = GRE_demotiki\nadd_popularity = { ideology = democratic popularity = 0.05 }\n",
      ai=2, filters=["FOCUS_FILTER_RESEARCH", "FOCUS_FILTER_POLITICAL"])
focus("GRE_restore_the_acropolis", 17, 8, "GFX_goal_generic_national_unity", "Restore the Acropolis",
      "Aragonese officers used the Parthenon as a parade ground and the Erechtheion as a stable. Greek scaffolding now climbs its columns.",
      pre=[["GRE_katharevousa", "GRE_demotiki"]], avail="owns_state = 49",
      effect="add_stability = 0.05\nadd_war_support = 0.05\nadd_political_power = 50\n",
      filters=["FOCUS_FILTER_STABILITY"])

# ---------------- rebuilding Hellas (economy) ----------------
focus("GRE_the_reconstruction_ministry", 2, 6, "GFX_goal_generic_construction2", "The Reconstruction Ministry",
      "A ministry of engineers, bankers and shipowners is given one task: turn three liberated provinces into a country.",
      pre=[["GRE_industry_of_a_free_greece"]], effect="add_ideas = GRE_reconstruction_ministry\n",
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("GRE_the_athens_salonika_railway", 1, 7, "GFX_goal_generic_construct_infrastructure", "The Athens-Salonika Railway",
      "The line was cut in a dozen places during the uprising. Rebuilt, it will tie the south to the north for good.",
      pre=[["GRE_the_reconstruction_ministry"]],
      effect=build(49, "infrastructure", 1) + build(100, "infrastructure", 1) + build(70, "infrastructure", 1),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("GRE_the_laurium_mines", 3, 7, "GFX_goal_generic_construct_military", "The Laurium Mines",
      "The silver of Laurium paid for the fleet that won at Salamis. Its old shafts still hold lead, iron and zinc.",
      pre=[["GRE_the_reconstruction_ministry"]], avail="owns_state = 49",
      effect="add_resource = { type = steel amount = 6 state = 49 }\nadd_resource = { type = aluminium amount = 2 state = 49 }\n",
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("GRE_the_port_of_piraeus", 0, 8, "GFX_goal_generic_construct_naval_dockyard", "The Port of Piraeus",
      "The great harbour of Athens was a dead dock under Aragon. Greek merchant captains are coming home to it.",
      pre=[["GRE_the_athens_salonika_railway"]], avail="owns_state = 49",
      effect=build(49, "dockyard", 1, 1) + build(49, "industrial_complex", 1, 1), filters=["FOCUS_FILTER_INDUSTRY"])
focus("GRE_the_thessalian_granary", 2, 8, "GFX_goal_generic_production", "The Thessalian Granary",
      "The plain of Thessaly can feed all of Greece, if its estates are worked instead of requisitioned.",
      pre=[["GRE_the_athens_salonika_railway"], ["GRE_the_laurium_mines"]], avail="owns_state = 100",
      effect="add_stability = 0.05\n" + build(100, "industrial_complex", 1, 1), filters=["FOCUS_FILTER_INDUSTRY", "FOCUS_FILTER_STABILITY"])
focus("GRE_salonika_tobacco", 4, 8, "GFX_goal_generic_trade", "The Salonika Tobacco Monopoly",
      "Macedonian tobacco is the finest in the Mediterranean. A state monopoly will turn its smoke into rifles.",
      pre=[["GRE_the_laurium_mines"]], avail="owns_state = 70",
      effect="add_political_power = 50\n" + build(70, "arms_factory", 1, 1), filters=["FOCUS_FILTER_INDUSTRY"])
focus("GRE_a_modern_greek_economy", 2, 9, "GFX_goal_generic_production", "A Modern Greek Economy",
      "Greece is no longer a bandit kingdom on a peninsula. It has ports, rails, mines and factories, and it means to keep them.",
      pre=[["GRE_the_port_of_piraeus", "GRE_the_thessalian_granary", "GRE_salonika_tobacco"]],
      effect="remove_ideas = GRE_reconstruction_ministry\nadd_ideas = GRE_modern_economy\n", filters=["FOCUS_FILTER_INDUSTRY"])

# ---------------- the Royal Hellenic Army (after the uprising) ----------------
focus("GRE_from_insurgents_to_army", 21, 4, "GFX_goal_generic_allies_build_infantry", "From Insurgents to an Army",
      "Bands of klephts, refugee volunteers and deserters from the Aragonese garrisons must become regiments with numbers, officers and supply.",
      pre=[["GRE_the_great_uprising"]], effect="army_experience = 20\n" + tech("GRE_from_insurgents_to_army", "infantry_weapons", 0.5, 1),
      filters=["FOCUS_FILTER_ARMY_XP", "FOCUS_FILTER_RESEARCH"])
focus("GRE_the_evelpidon_academy", 20, 5, "GFX_goal_generic_army_doctrines", "Reopen the Evelpidon",
      "The military academy of the Evelpidon, closed for a generation, reopens its doors. Its first class are veterans of the uprising.",
      pre=[["GRE_from_insurgents_to_army"]], effect="army_experience = 10\n" + tech("GRE_the_evelpidon_academy", "land_doctrine", 0.5, 1),
      filters=["FOCUS_FILTER_ARMY_XP", "FOCUS_FILTER_RESEARCH"])
focus("GRE_the_olympus_line", 22, 5, "GFX_goal_generic_defence", "The Olympus Line",
      "If Aragon comes again, it will have to climb. Concrete bunkers will line the passes of Olympus and the Pindus.",
      pre=[["GRE_from_insurgents_to_army"]],
      effect=bunker(70, "bunker", 2, "limit_to_border") + bunker(99, "bunker", 2, "limit_to_border") + bunker(100, "bunker", 1, "limit_to_border"),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("GRE_the_general_staff", 20, 6, "GFX_goal_generic_position_armies", "A Hellenic General Staff",
      "The uprising was won by brave men and luck. The next war will be won by planning.",
      pre=[["GRE_the_evelpidon_academy"]], effect="army_experience = 15\nadd_command_power = 25\n",
      filters=["FOCUS_FILTER_ARMY_XP"])
focus("GRE_aegean_coastal_batteries", 22, 6, "GFX_goal_generic_fortify_city", "Aegean Coastal Batteries",
      "Guns on every headland from Piraeus to Monemvasia. No Aragonese fleet will land troops in Greece unopposed again.",
      pre=[["GRE_the_olympus_line"]],
      effect=bunker(49, "coastal_bunker", 1, "limit_to_coastal") + bunker(50, "coastal_bunker", 1, "limit_to_coastal") + bunker(62, "coastal_bunker", 1, "limit_to_coastal"),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("GRE_the_royal_hellenic_navy", 22, 7, "GFX_goal_generic_build_navy", "A Hellenic Navy",
      "A nation of islands and sailors cannot live on fishing boats forever. The first Greek destroyers are laid down at Piraeus.",
      pre=[["GRE_aegean_coastal_batteries"]],
      effect="navy_experience = 25\n" + tech("GRE_the_royal_hellenic_navy", "naval_doctrine", 0.5, 1) + tech("GRE_hellenic_submarines", "ss_tech", 0.5, 1),
      filters=["FOCUS_FILTER_NAVY_XP", "FOCUS_FILTER_RESEARCH"])
focus("GRE_an_army_of_all_hellenes", 20, 7, "GFX_goal_generic_army_artillery", "An Army of All Hellenes",
      "Royalist and republican, Macedonian and Moreot, islander and mountaineer: one army, one oath, one flag.",
      pre=[["GRE_the_general_staff"]], effect="add_ideas = GRE_army_of_all_hellenes\n",
      filters=["FOCUS_FILTER_MANPOWER"])

# ---------------- the crown's regime (kingdom path) ----------------
focus("GRE_the_question_of_the_crown", 5, 6, "GFX_goal_generic_political_pressure", "The Question of the Crown",
      "King Andreas is old and tired, and the court is crowded with men who want to govern in his name. Greece must decide how a king rules a free people.",
      pre=[["GRE_the_king_in_athens"]], effect="add_political_power = 50\n", filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_the_kings_peace", 3, 7, "GFX_focus_rom_royal_dictatorship", "The King's Peace",
      "No parties and no generals. The king will govern with the Holy Synod and his council, as a father governs a household.",
      pre=[["GRE_the_question_of_the_crown"]], excl=["GRE_the_generals_regime", "GRE_the_constitutional_crown"],
      effect="add_ideas = GRE_throne_and_altar\nadd_popularity = { ideology = absolutist popularity = 0.1 }\n",
      ai=5, filters=["FOCUS_FILTER_POLITICAL", "FOCUS_FILTER_STABILITY"])
focus("GRE_the_generals_regime", 5, 7, "GFX_goal_support_fascism", "The Twelfth of March",
      "General Ioannis Varvakis, hero of Florina, has no patience for courtiers or parliaments. With the king's reluctant signature, he suspends the constitution and proclaims a regime of National Regeneration.",
      pre=[["GRE_the_question_of_the_crown"]], excl=["GRE_the_kings_peace", "GRE_the_constitutional_crown"],
      effect=("set_party_name = { ideology = fascism long_name = GRE_fascism_party_varvakis_long name = GRE_fascism_party_varvakis }\n"
              "set_politics = { ruling_party = fascism elections_allowed = no }\n"
              "set_popularities = { fascism = 55 absolutist = 35 democratic = 10 }\n"
              + leader("GRE_ioannis_varvakis") + "set_cosmetic_tag = GRE_hellenic_state\nadd_ideas = GRE_national_regeneration\n"),
      ai=2, filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_the_constitutional_crown", 7, 7, "GFX_focus_generic_treaty", "The Constitutional Crown",
      "The king will reign, but parliament will govern. Theodoros Mavrogenis, leader of the moderates who kept the royalist committees alive, becomes the first Prime Minister of a free Greece.",
      pre=[["GRE_the_question_of_the_crown"]], excl=["GRE_the_kings_peace", "GRE_the_generals_regime"],
      effect=("set_party_name = { ideology = democratic long_name = GRE_democratic_party_mavrogenis_long name = GRE_democratic_party_mavrogenis }\n"
              "set_politics = { ruling_party = democratic elections_allowed = yes last_election = \"1936.1.1\" election_frequency = 48 }\n"
              "set_popularities = { democratic = 55 absolutist = 40 fascism = 5 }\n"
              + leader("GRE_theodoros_mavrogenis") + "add_ideas = GRE_constitutional_crown\n"),
      ai=2, filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_the_holy_synod", 3, 8, "GFX_goal_generic_national_unity", "The Holy Synod",
      "The bishops of the Church of Greece sit at the king's council table, and every pulpit preaches loyalty to the crown.",
      pre=[["GRE_the_kings_peace"]], effect="add_stability = 0.1\nadd_political_power = 50\n", filters=["FOCUS_FILTER_STABILITY"])
focus("GRE_the_youth_of_hellas", 5, 8, "GFX_goal_generic_propaganda", "The Youth of Hellas",
      "Every boy and girl in Greece will march, drill and sing for the nation. Varvakis wants a generation that will never be conquered again.",
      pre=[["GRE_the_generals_regime"]], effect="add_war_support = 0.1\nadd_manpower = 10000\n",
      filters=["FOCUS_FILTER_WAR_SUPPORT", "FOCUS_FILTER_MANPOWER"])
focus("GRE_the_vouli_reconvenes", 7, 8, "GFX_goal_support_democracy", "The Vouli Reconvenes",
      "For the first time since the Aragonese occupation, the Hellenic Parliament meets in Athens. Royalists and republicans shout at each other, and it is wonderful.",
      pre=[["GRE_the_constitutional_crown"]], effect="add_stability = 0.05\nadd_political_power = 100\n",
      filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_long_live_the_king", 5, 9, "GFX_focus_hun_elect_a_king", "Long Live the King",
      "Whatever the government, the crown endures. King Andreas abdicates in favour of Crown Prince Konstantinos, and the young king is crowned in the cathedral of Athens. Under the King's Peace he rules in person; otherwise he reigns over the government Greece has chosen.",
      pre=[["GRE_the_holy_synod", "GRE_the_youth_of_hellas", "GRE_the_vouli_reconvenes"]],
      effect=("add_stability = 0.1\nadd_war_support = 0.05\nadd_political_power = 50\n"
              "if = { limit = { has_government = absolutist }\n"
              "\tif = { limit = { NOT = { has_character = GRE_konstantinos_kolokotronis } } recruit_character = GRE_konstantinos_kolokotronis }\n"
              "\tpromote_character = GRE_konstantinos_kolokotronis\n}\n"),
      filters=["FOCUS_FILTER_STABILITY"])

# ---------------- the republic (republican path) ----------------
focus("GRE_president_karavias", 10, 6, "GFX_goal_support_democracy", "President Karavias",
      "Alexandros Karavias led the Athenian rebels in the uprising. With the union done, the united parliament elects him President of the Hellenic Republic.",
      pre=[["GRE_union_with_the_republic"]],
      effect=leader("GRE_alexandros_karavias") + "set_cosmetic_tag = GRE_hellenic_republic\nadd_stability = 0.05\n",
      filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_exile_the_dynasty", 10, 7, "GFX_goal_generic_territory_or_war", "Exile the Kolokotronis",
      "A republic cannot share a country with a king who might want his throne back. King Andreas and his family are put on a ship to Alexandria.",
      pre=[["GRE_president_karavias", "GRE_a_constitution_for_hellas"]], excl=["GRE_a_royal_pension"],
      effect="add_popularity = { ideology = democratic popularity = 0.1 }\nadd_stability = -0.05\nadd_political_power = 100\n",
      ai=1, filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_a_royal_pension", 12, 7, "GFX_focus_generic_treaty", "A Royal Pension",
      "The old king gave up his crown for Greece. He will keep his title, his villa at Polygyros and the gratitude of the republic.",
      pre=[["GRE_president_karavias", "GRE_a_constitution_for_hellas"]], excl=["GRE_exile_the_dynasty"],
      effect="add_stability = 0.1\nadd_popularity = { ideology = absolutist popularity = -0.05 }\n",
      ai=2, filters=["FOCUS_FILTER_STABILITY"])
focus("GRE_land_reform_in_thessaly", 11, 8, "GFX_goal_generic_production", "Land Reform in Thessaly",
      "The great estates of Thessaly, many confiscated by Aragonese officers, are broken up and given to the families who work them.",
      pre=[["GRE_exile_the_dynasty", "GRE_a_royal_pension"]], effect="add_ideas = GRE_land_reform\n",
      filters=["FOCUS_FILTER_STABILITY", "FOCUS_FILTER_MANPOWER"])
focus("GRE_the_second_hellenic_republic", 11, 9, "GFX_goal_generic_national_unity", "The Second Hellenic Republic",
      "A century after the first Hellenic Republic of Kapodistrias, the second is here to stay.",
      pre=[["GRE_land_reform_in_thessaly"]], effect="add_ideas = GRE_second_republic\n", filters=["FOCUS_FILTER_STABILITY", "FOCUS_FILTER_RESEARCH"])

EXTRA_IDEAS = [
    ("GRE_blessing_of_athos", "generic_pp_unity_bonus", "stability_factor = 0.05\nwar_support_factor = 0.05",
     "Blessing of the Holy Mountain", "The monks of Athos pray for the liberation of Greece, and every Greek knows it."),
    ("GRE_reconstruction_ministry", "generic_production_bonus", "production_speed_buildings_factor = 0.1\nconsumer_goods_factor = 0.05",
     "The Reconstruction Ministry", "Rebuilding a war-torn country is expensive, but it is being done."),
    ("GRE_modern_economy", "generic_production_bonus", "industrial_capacity_factory = 0.05\nproduction_speed_buildings_factor = 0.05",
     "A Modern Greek Economy", "Ports, rails, mines and factories."),
    ("GRE_katharevousa", "generic_pp_unity_bonus", "political_power_gain = 0.1\nstability_factor = 0.03",
     "Katharevousa", "The state writes in the purified Greek of the courts and the Church."),
    ("GRE_demotiki", "generic_research_bonus", "research_speed_factor = 0.04\nmonthly_population = 0.05",
     "Demotiki", "The state writes and teaches the Greek its people speak."),
    ("GRE_army_of_all_hellenes", "generic_infantry_bonus", "army_org_factor = 0.05\ntraining_time_army_factor = -0.1",
     "An Army of All Hellenes", "One army, one oath, one flag."),
    ("GRE_throne_and_altar", "generic_pp_unity_bonus", "stability_factor = 0.1\npolitical_power_gain = 0.1\ndrift_defence_factor = 0.2",
     "Throne and Altar", "King and Church govern Greece together."),
    ("GRE_national_regeneration", "generic_fascism_drift_bonus", "war_support_factor = 0.1\nconscription = 0.01\nstability_factor = -0.05",
     "National Regeneration", "General Varvakis promises a Greece that will never be conquered again, and a Greece that does what it is told."),
    ("GRE_constitutional_crown", "generic_democratic_drift_bonus", "stability_factor = 0.1\npolitical_power_gain = 0.05",
     "The Constitutional Crown", "The king reigns; parliament governs."),
    ("GRE_land_reform", "generic_agrarian_society", "stability_factor = 0.05\nmonthly_population = 0.1",
     "Land to the Tillers", "The estates of Thessaly belong to those who work them."),
    ("GRE_second_republic", "generic_democratic_drift_bonus", "stability_factor = 0.05\npolitical_power_gain = 0.1\nresearch_speed_factor = 0.03",
     "The Second Hellenic Republic", "A free republic of all the Greeks."),
]

# ---------------- characters ----------------
def portrait(gfx, kind="civilian"):
    return f"\t\tportraits={{\n\t\t\t{kind}={{\n\t\t\t\tlarge=\"{gfx}\"\n\t\t\t\tsmall=\"{gfx}_small\"\n\t\t\t}}\n\t\t}}\n"
CHARS = []
def leader_char(key, name, gfx, ideology):
    CHARS.append((key, name, portrait(gfx) + f"\t\tcountry_leader={{\n\t\t\tideology={ideology}\n\t\t\texpire=\"1965.1.1.1\"\n\t\t\tid=-1\n\t\t}}\n"))
def advisor_char(key, name, gfx, slot, trait, focus_id, cost=150):
    CHARS.append((key, name, portrait(gfx) + f"\t\tadvisor={{\n\t\t\tslot = {slot}\n\t\t\tidea_token = {key}\n"
        f"\t\t\tallowed = {{ original_tag = GRE }}\n\t\t\tavailable = {{ has_completed_focus = {focus_id} }}\n"
        f"\t\t\ttraits = {{ {trait} }}\n\t\t\tcost = {cost}\n\t\t\tai_will_do = {{ factor = 1 }}\n\t\t}}\n"))
def general_char(key, name, gfx, skill, atk, dfn, plan, log, traits):
    CHARS.append((key, name, portrait(gfx, "army") + f"\t\tcorps_commander={{\n\t\t\ttraits={{ {traits} }}\n\t\t\tskill={skill}\n"
        f"\t\t\tattack_skill={atk}\n\t\t\tdefense_skill={dfn}\n\t\t\tplanning_skill={plan}\n\t\t\tlogistics_skill={log}\n\t\t\tlegacy_id=0\n\t\t}}\n"))

leader_char("GRE_ioannis_varvakis", "Ioannis Varvakis", "GFX_GRE_Ioannis_Metaxas_KR", "fascism_ideology")
leader_char("GRE_theodoros_mavrogenis", "Theodoros Mavrogenis", "GFX_GRE_Konstantinos_Tsaldaris", "conservatism")
leader_char("GRE_alexandros_karavias", "Alexandros Karavias", "GFX_GRE_Alexandros_Papanastasiou", "liberalism")
advisor_char("GRE_spyridon_valaoritis", "Spyridon Valaoritis", "GFX_GRE_Stylianos_Lykoudis", "political_advisor", "silent_workhorse", "GRE_the_court_at_polygyros")
advisor_char("GRE_metropolitan_chrysanthos", "Metropolitan Chrysanthos", "GFX_GRE_Panagiotis_Kanellopoulos", "political_advisor", "popular_figurehead", "GRE_the_holy_mountain")
advisor_char("GRE_spyridon_laskaris", "Spyridon Laskaris", "GFX_GRE_Themistoklis_Sofoulis", "political_advisor", "captain_of_industry", "GRE_the_reconstruction_ministry")
advisor_char("GRE_nikolaos_zervakis", "Nikolaos Zervakis", "GFX_GRE_Konstantinos_Tsatsos", "political_advisor", "fortification_engineer", "GRE_the_olympus_line", 100)
advisor_char("GRE_periklis_rallis", "Periklis Rallis", "GFX_GRE_Stefanos_Sarafis", "theorist", "military_theorist", "GRE_the_evelpidon_academy")
advisor_char("GRE_alexandros_rodios", "Alexandros Rodios", "GFX_GRE_Alexandros_Papagos", "army_chief", "army_chief_defensive_1", "GRE_the_general_staff")
general_char("GRE_konstantinos_kolokotronis", "Crown Prince Konstantinos", "GFX_GRE_Paul", 3, 3, 2, 2, 2, "trickster")
k, n, body = CHARS[-1]
body = body.replace("\t\tportraits={\n", "\t\tportraits={\n\t\t\tcivilian={\n\t\t\t\tlarge=\"GFX_GRE_Paul\"\n\t\t\t\tsmall=\"GFX_GRE_Paul_small\"\n\t\t\t}\n", 1)
body += "\t\tcountry_leader={\n\t\t\tideology=absolute_monarchy\n\t\t\texpire=\"1975.1.1.1\"\n\t\t\tid=-1\n\t\t}\n"
CHARS[-1] = (k, n, body)
general_char("GRE_giorgos_zachos", "Kapetan Giorgos Zachos", "GFX_GRE_Manolis_Mantakas", 2, 3, 2, 1, 1, "trickster")

cs = "characters={\n"
for key, _, body in CHARS:
    cs += f"\t{key}={{\n\t\tname={key}\n" + body + "\t}\n\n"
cs += "}\n"
open(J("common/characters/GRE_focus_characters.txt"), "w", encoding="utf-8", newline="\n").write(cs)

EXTRA_LOC = [f' {key}:0 "{name}"' for key, name, _ in CHARS] + [
 ' GRE_hellenic_state:0 "Hellenic State"', ' GRE_hellenic_state_ADJ:0 "Hellenic"', ' GRE_hellenic_state_DEF:0 "the Hellenic State"',
 ' GRE_hellenic_republic:0 "Hellenic Republic"', ' GRE_hellenic_republic_ADJ:0 "Hellenic"', ' GRE_hellenic_republic_DEF:0 "the Hellenic Republic"',
 ' GRE_fascism_party_varvakis:0 "EAK"', ' GRE_fascism_party_varvakis_long:0 "Ethniki Anagennisis Kinima (National Regeneration Movement)"',
 ' GRE_democratic_party_mavrogenis:0 "Laiko Komma"', ' GRE_democratic_party_mavrogenis_long:0 "Laiko Komma (People\'s Party)"',
]
# ---------------- emit focus tree ----------------
def indent(text, n):
    pad = "\t" * n
    return "".join(pad + l + "\n" if l.strip() else "\n" for l in text.strip("\n").split("\n"))
# keep the economy/army column on the left, push everything else right so branches do not collide
LEFT = {"GRE_rebuild_polygyros", "GRE_aegean_fishing_fleets", "GRE_the_klephts", "GRE_the_evzones", "GRE_mountain_warfare",
        "GRE_the_diaspora_volunteers", "GRE_industry_of_a_free_greece", "GRE_the_reconstruction_ministry",
        "GRE_the_athens_salonika_railway", "GRE_the_laurium_mines", "GRE_the_port_of_piraeus", "GRE_the_thessalian_granary",
        "GRE_salonika_tobacco", "GRE_a_modern_greek_economy"}
for f in F:
    if f["id"] not in LEFT: f["x"] += 3
out = ["focus_tree = {\n\tid = GRE_focus\n\n\tcountry = {\n\t\tfactor = 0\n\t\tmodifier = {\n\t\t\tadd = 10\n\t\t\toriginal_tag = GRE\n\t\t}\n\t}\n\n\tdefault = no\n\n\tinitial_show_position = { focus = GRE_the_last_free_greeks }\n\n"]
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
open(J("common/national_focus/GRE_NF.txt"), "w", encoding="utf-8", newline="\n").write("".join(out))

# ---------------- ideas ----------------
IDEAS = [
    ("GRE_the_great_uprising", "generic_war_of_national_liberation", "war_support_factor = 0.15\nconscription = 0.02\nstability_factor = 0.1\narmy_defence_factor = 0.15\narmy_core_defence_factor = 0.1",
     "The Great Uprising", "All of Greece is in arms against Aragon."),
    ("GRE_klephts", "warrior_traditions_idea", "army_defence_factor = 0.05\nspecial_forces_cap = 0.1",
     "The Klephts", "Greek soldiers fight like the mountain guerrillas of old."),
    ("GRE_march_on_athens", "generic_infantry_bonus", "army_attack_factor = 0.1\nwar_support_factor = 0.05",
     "The March on Athens", "With Aragon gone, the whole royal army turns south against the republic."),
    ("GRE_hellenic_constitution", "generic_democratic_drift_bonus", "stability_factor = 0.1\npolitical_power_gain = 0.1",
     "A Constitution for Hellas", "Greece is governed by a written constitution and a freely elected parliament."),
    ("GRE_hellas_reborn", "generic_national_unification", "stability_factor = 0.1\nwar_support_factor = 0.1\nindustrial_capacity_factory = 0.05",
     "Hellas Reborn", "Greece is free and united."),
]
IDEAS += EXTRA_IDEAS
s = "ideas = {\n\tcountry = {\n"
for key, pic, mod, _, _ in IDEAS:
    s += f"\t\t{key} = {{\n\t\t\tpicture = {pic}\n\t\t\tallowed = {{ always = no }}\n\t\t\tremoval_cost = -1\n\t\t\tmodifier = {{\n" + indent(mod, 4) + "\t\t\t}\n\t\t}\n"
s += ("\t\tSPC_greek_insurgency = {\n\t\t\tpicture = generic_army_problems\n\t\t\tallowed = { always = no }\n\t\t\tremoval_cost = -1\n"
      "\t\t\tmodifier = {\n\t\t\t\tstability_factor = -0.1\n\t\t\t\twar_support_factor = -0.05\n\t\t\t\tpolitical_power_gain = -0.1\n\t\t\t}\n\t\t}\n")
s += "\t}\n}\n"
open(J("common/ideas/GRE_focus_ideas.txt"), "w", encoding="utf-8", newline="\n").write(s)

# ---------------- events ----------------
EV = '''add_namespace = greek_uprising

# Aragon learns of the uprising
country_event = {
	id = greek_uprising.1
	title = greek_uprising.1.t
	desc = greek_uprising.1.d
	picture = GFX_report_event_chinese_soldiers_fighting
	is_triggered_only = yes

	option = {
		name = greek_uprising.1.a
		add_war_support = 0.05
		add_timed_idea = { idea = SPC_greek_insurgency days = 730 }
		country_event = { id = greek_uprising.2 days = 365 }
		country_event = { id = greek_uprising.10 days = 7 }
	}
}

# Aragon: negotiate or fight on (first after 1 year, then every 3 weeks while the revolt lasts)
country_event = {
	id = greek_uprising.2
	title = greek_uprising.2.t
	desc = greek_uprising.2.d
	picture = GFX_report_event_journalists_speech
	is_triggered_only = yes

	trigger = {
		NOT = { has_country_flag = SPC_greek_peace }
		OR = {
			has_war_with = GRE
			has_war_with = HEL
		}
	}

	option = {
		name = greek_uprising.2.a
		set_country_flag = SPC_greek_peace
		if = {
			limit = { has_war_with = GRE }
			white_peace = GRE
			GRE = { country_event = { id = greek_uprising.5 } }
		}
		if = {
			limit = { has_war_with = HEL }
			white_peace = HEL
			HEL = { country_event = { id = greek_uprising.5 } }
		}
		remove_ideas = SPC_greek_insurgency
		add_war_support = -0.05
		ai_chance = {
			base = 20
			modifier = { factor = 4 has_war_with = OCC }
			modifier = { factor = 2 has_stability < 0.4 }
		}
	}

	option = {
		name = greek_uprising.2.b
		add_war_support = 0.02
		country_event = { id = greek_uprising.2 days = 21 }
		ai_chance = { base = 80 }
	}
}

# Aragon: the revolt has been crushed
country_event = {
	id = greek_uprising.3
	title = greek_uprising.3.t
	desc = greek_uprising.3.d
	picture = GFX_report_event_soldiers_marching
	is_triggered_only = yes

	option = {
		name = greek_uprising.3.a
		set_country_flag = SPC_greek_peace
		remove_ideas = SPC_greek_insurgency
		add_stability = 0.1
		add_war_support = 0.05
	}
}

# Greek side: Aragon recognises independence
country_event = {
	id = greek_uprising.5
	title = greek_uprising.5.t
	desc = greek_uprising.5.d
	picture = GFX_report_event_iww_demonstration
	is_triggered_only = yes

	option = {
		name = greek_uprising.5.a
		add_stability = 0.1
		add_political_power = 100
	}
}

# Hidden weekly check: has Aragon crushed every rebel government?
country_event = {
	id = greek_uprising.10
	hidden = yes
	is_triggered_only = yes

	immediate = {
		if = {
			limit = {
				NOT = { has_country_flag = SPC_greek_peace }
				NOT = { has_war_with = GRE }
				NOT = { has_war_with = HEL }
			}
			country_event = { id = greek_uprising.3 }
		}
		else_if = {
			limit = { NOT = { has_country_flag = SPC_greek_peace } }
			country_event = { id = greek_uprising.10 days = 7 }
		}
	}

	option = {
		name = greek_uprising.10.a
	}
}
'''
open(J("events/greek_uprising.txt"), "w", encoding="utf-8", newline="\n").write(EV)

# ---------------- OOBs ----------------
def oob(tag, name, units):
    s = ""
    if not tag.endswith("_extra"):
        s = "division_template = {\n\tname = \"%s\"\n\tregiments = {\n" % name
        for x in range(2):
            for y in range(3):
                s += f"\t\tinfantry = {{ x = {x} y = {y} }}\n"
        s += "\t}\n}\n\n"
    s += "units = {\n"
    for i, (label, prov) in enumerate(units, 1):
        s += f"\tdivision = {{\n\t\tname = \"{label}\"\n\t\tlocation = {prov}\n\t\tdivision_template = \"{name}\"\n\t\tstart_experience_factor = 0.5\n\t\tstart_equipment_factor = 1.0\n\t}}\n"
    s += "}\n"
    open(J("history/units", tag + ".txt"), "w", encoding="utf-8", newline="\n").write(s)
oob("GRE_uprising", "Royalist Insurgents", [("Salonika Legion", 11818), ("Macedonian Volunteers", 3526), ("Thessalian Insurgents", 3973), ("Florina Brigade", 9837), ("Volos Defenders", 3914), ("Sacred Band of Macedonia", 6990), ("Larissa Rifles", 3973), ("Kozani Mountaineers", 9837), ("Serres Volunteers", 11818), ("Kavala Guard", 3526)])
oob("GRE_uprising_extra", "Royalist Insurgents", [("Chalkidiki Rifles", 9791), ("Olympus Klephts", 863), ("Pindus Mountaineers", 841)])
oob("HEL_uprising", "Republican Militia", [("Athenian Republican Guard", 4109), ("Piraeus Workers' Militia", 976), ("Peloponnesian Militia", 10203), ("Aegean Volunteers", 6550), ("Spartan Republican Brigade", 4078), ("Euboea Militia", 1205), ("Marathon Brigade", 4109), ("Patras Workers' Brigade", 10203), ("Cyclades Volunteers", 6550), ("Argos Militia", 4078)])
oob("GRE_occitan_volunteers", "Occitan Volunteers", [("1st Occitan Volunteer Brigade", 895), ("2nd Occitan Volunteer Brigade", 3936)])
oob("HEL_uprising_extra", "Republican Militia", [("Corinth Militia", 1106), ("Attica Volunteers", 3864)])
oob("GRE_sacred_band", "Sacred Band", [("The Sacred Band", 895)])

# ---------------- localisation ----------------
def q(t): return t.replace('"', '\\"')
L = ["l_english:", " # Greece focus tree"]
for f in F:
    L.append(f' {f["id"]}:0 "{q(f["name"])}"'); L.append(f' {f["id"]}_desc:0 "{q(f["desc"])}"')
for key, _, _, name, desc in IDEAS:
    L.append(f' {key}:0 "{q(name)}"'); L.append(f' {key}_desc:0 "{q(desc)}"')
L += [
 ' SPC_greek_insurgency:0 "Greek Insurgency"',
 ' SPC_greek_insurgency_desc:0 "Greek rebels hold the mountains of Macedonia and the streets of Athens. Every garrison in Greece is under attack."',
 ' GRE_hellenic_alliance:0 "Hellenic Alliance"',
 ' greek_uprising.1.t:0 "Revolt in Greece!"',
 ' greek_uprising.1.d:0 "Signal fires burned on Mount Olympus last night. By morning, royalist insurgents had seized Salonika, Volos and Florina and declared for the King of Greece in Polygyros. In Athens, the Peloponnese and the islands, republican militias have proclaimed a Hellenic Republic and refuse to recognise the king. Our garrisons are cut off and under fire across the whole of Greece, though the two rebel governments are already fighting each other as well as us."',
 ' greek_uprising.1.a:0 "Crush the traitors!"',
 ' greek_uprising.2.t:0 "The Greek Question"',
 ' greek_uprising.2.d:0 "A year of fighting has not broken the Greek rebels. Our garrisons are pinned down, the foreign press reports every burned village, and the generals warn that the army is needed elsewhere. Some ministers now quietly suggest that Greece is not worth the cost: recognise the rebel governments and bring the troops home."',
 ' greek_uprising.2.a:0 "Let Greece go. Aragon has bigger enemies."',
 ' greek_uprising.2.b:0 "Never! Not one village will be surrendered."',
 ' greek_uprising.3.t:0 "The Greek Revolt Crushed"',
 ' greek_uprising.3.d:0 "The last rebel strongholds have fallen. Royalist and republican leaders alike have fled into exile or been captured. Order is restored across Greece, and the army can finally turn its attention back to Occitania."',
 ' greek_uprising.3.a:0 "Aragon endures."',
 ' greek_uprising.5.t:0 "Aragon Recognises Greek Independence"',
 ' greek_uprising.5.d:0 "Unable to break our resistance, the Aragonese government has agreed to a ceasefire and withdrawn its garrisons. For the first time in generations, Greeks govern Greek lands. But the war between the royalists of Polygyros and the republicans of Athens goes on: only one of them will rule a free Greece."',
 ' greek_uprising.5.a:0 "Zito i Ellas!"',
 ' greek_uprising.10.a:0 "OK"',
 ' # Hellenic Republic',
 ' HEL:0 "Hellenic Republic"', ' HEL_ADJ:0 "Hellenic"', ' HEL_DEF:0 "the Hellenic Republic"',
 ' HEL_democratic:0 "Hellenic Republic"', ' HEL_democratic_ADJ:0 "Hellenic"', ' HEL_democratic_DEF:0 "the Hellenic Republic"',
 ' HEL_absolutist:0 "Hellenic State"', ' HEL_absolutist_ADJ:0 "Hellenic"', ' HEL_absolutist_DEF:0 "the Hellenic State"',
 ' HEL_fascism:0 "Hellenic State"', ' HEL_fascism_ADJ:0 "Hellenic"', ' HEL_fascism_DEF:0 "the Hellenic State"',
 ' HEL_neutrality:0 "Hellenic Republic"', ' HEL_neutrality_ADJ:0 "Hellenic"', ' HEL_neutrality_DEF:0 "the Hellenic Republic"',
 ' HEL_democratic_party:0 "Republican Union"', ' HEL_democratic_party_long:0 "Republican Union of Hellas"',
 ' HEL_absolutist_party:0 "Royalists"', ' HEL_fascism_party:0 "National Front"', ' HEL_neutrality_party:0 "Independents"',
 ' HEL_alexandros_karavias:0 "Alexandros Karavias"',
] + EXTRA_LOC
open(J("localisation/english/GRE_focus_l_english.yml"), "w", encoding="utf-8-sig", newline="\n").write("\n".join(L) + "\n")
print(len(F), "GRE focuses")
