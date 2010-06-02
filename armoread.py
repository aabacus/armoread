#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Armoread is used to read information from the WoW Armory about guilds, 
characters and items.

armoread.py
    -h, --help              Show help - what you are reading now.
    -v, --verbose           Be verbose and print what's being done.
    -w                      Write stuff to file(s)
    -f, --force             Force writing (ie overwrite file if already exist).
    -r ..., --realm=...     Set realm.
    -g ..., --guild=...     Set guild.
                            If -w is specified AND neither -c nor -i is,
                            it will result in guild info written to one file:
                                <guild-name>.xml
    -c ..., --char=...      Set char - several chars can be specified.
                            If -w is specified will result in one file:
                                <char-name>.xml
    -i ..., --itemid=...    Set item - several items can be specified.
                            If -w is specified will result in two files:
                                <itemid>.xml
                                <itemid>-tooltip.xml
    --eu, --us              Set area (EU or US). Used to pick which armory
                            to read from.
    --gs, --gearscore       Calculate the gear score for involved characters.

Status: far from done, slightly useful =)
Working: grabbing char-info and dump it to xml file.
    Example:
        python armoread.py -w -c Aabacus -c Absolutus
    => Aabacus.xml Absolutus.xml

TODO:
    -f
        Force overwriting of files.
    --gs, --gearscore
        Calculate gear score for selected chars.
    --gdir, --cdir, --idir
        Support flag to specify subdirectories (now hard coded to ./items,
    --mkdir
        Make dirs if they don't exist.
    ./guilds, ./chars)
    --no-online
        Don't go online! Read what can be read from existing files.
"""

import sys
import getopt
import codecs
import urllib2
import xml.dom.minidom as xdm

#USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-GB; rv:1.8.1.4) Gecko/20070515 Firefox/2.0.0.4'
USER_AGENT = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.8) Gecko/20101337 Gentoo Firefox/3.5.8'
BASE_URLs = {'EU':'http://eu.wowarmory.com/', 'US':'http://www.wowarmory.com/'}
SERVER_AREA = 'EU'
FILE_ENCODING = "utf-8"

class Guild(object):

    def __init__(self, guild='', realm='', base_url=BASE_URLs[SERVER_AREA], dom=None):
        self.dom = dom
        self.base_url = base_url
        self.realm = realm
        self.name = guild

    def parse(self, node):
        elements = [e for e in dom.childNodes
                if e.nodeType == e.ELEMENT_NODE]
        for node in elements:
            method = getattr(self, "parse_%s" % node.__class__.__name__)
            method(node)

    def parse_page(self, node):
        for node in node.getElementsByTagName("guildInfo"):
            parse_guildInfo(node)

    def parse_guildInfo(self, node):
        pass

    def parse_guild(self, node):
        pass

    def parse_members(self, node):
        pass

    def parse_character(self, node):
        pass


class Stats(object):
    def __init__(self):
        e_character = {
            "battleGroup": "Reckoning / Abrechnung",
            "charUrl": "r=Trollbane&amp;cn=Aabacus",
            "class": "Warrior",
            "classId": "1",
            "classUrl": "c=Warrior",
            "faction": "Alliance",
            "factionId": "0",
            "gender": "Female",
            "genderId": "1",
            "guildName": "Emerge",
            "guildUrl": "r=Trollbane&amp;gn=Emerge",
            "lastModified": "May 15, 2010",
            "level": "80",
            "name": "Aabacus",
            "points": "3080",
            "prefix": "",
            "race": "Night Elf",
            "raceId": "4",
            "realm": "Trollbane",
            "suffix": " the Patient",
            "titleId": "137"
            }
        e_active_talentSpecs = 1
        e_talentSpecs_1 = [14, 3, 54]
            #"active"="1" 
            #"icon"="inv_shield_06" "prim"="Protection" "treeOne"="14" "treeThree"="54" "treeTwo"="3"}
        e_talentSpecs_2 = [19, 52, 0]
            #"icon"="ability_warrior_innerrage" "prim"="Fury" "treeOne"="19" "treeThree"="0" "treeTwo"="52"}
        e_professions = {
                "0": {"id": "164", "key": "blacksmithing", "max": "450", "name": "Blacksmithing", "value": "450"},
                "1": {"id": "755", "key": "jewelcrafting", "max": "450", "name": "Jewelcrafting", "value": "450"}
            }
        """
			<characterBars>
				<health effective="44226"/>
				<secondBar casting="-1" effective="100" notCasting="-1" perFive="-1" type="r"/>
			</characterBars>
			<baseStats>
				<strength attack="3410" base="180" block="85" effective="1715"/>
				<agility armor="298" attack="-1" base="117" critHitPercent="5.57" effective="149"/>
				<stamina base="173" effective="3601" health="35830" petBonus="-1"/>
				<intellect base="36" critHitPercent="-1.00" effective="46" mana="-1" petBonus="-1"/>
				<spirit base="59" effective="69" healthRegen="40" manaRegen="-1"/>
				<armor base="31686" effective="31911" percent="67.69" petBonus="-1"/>
			</baseStats>
			<resistances>
				<arcane petBonus="-1" value="0"/>
				<fire petBonus="-1" value="0"/>
				<frost petBonus="-1" value="0"/>
				<holy petBonus="-1" value="0"/>
				<nature petBonus="-1" value="0"/>
				<shadow petBonus="-1" value="0"/>
			</resistances>
			<melee>
				<mainHandDamage dps="594.6" max="1067" min="836" percent="0" speed="1.60"/>
				<offHandDamage dps="0.0" max="0" min="0" percent="0" speed="2.00"/>
				<mainHandSpeed hastePercent="0.00" hasteRating="0" value="1.60"/>
				<offHandSpeed hastePercent="0.00" hasteRating="0" value="2.00"/>
				<power base="4536" effective="4536" increasedDps="324.0"/>
				<hitRating increasedHitPercent="7.56" penetration="0" reducedArmorPercent="0.00" value="248"/>
				<critChance percent="5.57" plusPercent="0.00" rating="0"/>
				<expertise additional="16" percent="5.50" rating="132" value="22"/>
			</melee>
			<ranged>
				<weaponSkill rating="0" value="0"/>
				<damage dps="297.7" max="767" min="483" percent="0" speed="2.10"/>
				<speed hastePercent="0.00" hasteRating="0" value="2.10"/>
				<power base="219" effective="219" increasedDps="15.0" petAttack="-1.00" petSpell="-1.00"/>
				<hitRating increasedHitPercent="7.56" penetration="0" reducedArmorPercent="0.00" value="248"/>
				<critChance percent="0.00" plusPercent="0.00" rating="0"/>
			</ranged>
			<spell>
				<bonusDamage>
					<arcane value="0"/>
					<fire value="0"/>
					<frost value="0"/>
					<holy value="0"/>
					<nature value="0"/>
					<shadow value="0"/>
					<petBonus attack="-1" damage="-1" fromType=""/>
				</bonusDamage>
				<bonusHealing value="0"/>
				<hitRating increasedHitPercent="9.45" penetration="0" reducedResist="0" value="248"/>
				<critChance rating="0">
					<arcane percent="0.00"/>
					<fire percent="0.00"/>
					<frost percent="0.00"/>
					<holy percent="0.00"/>
					<nature percent="0.00"/>
					<shadow percent="0.00"/>
				</critChance>
				<penetration value="0"/>
				<manaRegen casting="0.00" notCasting="0.00"/>
				<hasteRating hastePercent="0.00" hasteRating="0"/>
			</spell>
			<defenses>
				<armor base="31686" effective="31911" percent="67.69" petBonus="-1"/>
				<defense decreasePercent="5.96" increasePercent="5.96" plusDefense="149" rating="733" value="400.00"/>
				<dodge increasePercent="18.28" percent="29.97" rating="827"/>
				<parry increasePercent="11.56" percent="23.18" rating="523"/>
				<block increasePercent="2.56" percent="18.52" rating="42"/>
				<resilience damagePercent="0.00" hitPercent="0.00" value="0.00"/>
			</defenses>
			<items>
				<item displayInfoId="64570" durability="100" gem0Id="41380" gem1Id="40141" gem2Id="0" gemIcon0="inv_jewelcrafting_shadowspirit_02" gemIcon1="inv_jewelcrafting_gem_40" icon="inv_helmet_158" id="51218" level="264" maxDurability="100" name="Sanctified Ymirjar Lord's Greathelm" permanentEnchantIcon="ability_warrior_swordandboard" permanentEnchantItemId="44150" permanentenchant="3818" pickUp="PickUpLargeChain" putDown="PutDownLArgeChain" randomPropertiesId="0" rarity="4" seed="0" slot="0"/>
                [...]
			</items>
			<glyphs>
				<glyph effect="Increases your block value by 10% for 10 sec after using your Shield Slam ability." icon="ui-glyph-rune-20" id="502" name="Glyph of Blocking" type="major"/>
				<glyph effect="Increases the duration of your Commanding Shout ability by 2 min." icon="ui-glyph-rune-17" id="851" name="Glyph of Command" type="minor"/>
				<glyph effect="Increases the radius of your Thunder Clap ability by 2 yards." icon="ui-glyph-rune-2" id="487" name="Glyph of Thunder Clap" type="minor"/>
				<glyph effect="Your Devastate ability now applies two stacks of Sunder Armor." icon="ui-glyph-rune-4" id="493" name="Glyph of Devastate" type="major"/>
				<glyph effect="Increases the range of your Charge ability by 5 yards." icon="ui-glyph-rune-5" id="485" name="Glyph of Charge" type="minor"/>
				<glyph effect="Increases the chance for your Taunt ability to succeed by 8%." icon="ui-glyph-rune-15" id="506" name="Glyph of Taunt" type="major"/>
			</glyphs>
            """

class Character(object):

    def __init__(self, character_name="", realm='', base_url=BASE_URLs[SERVER_AREA], dom=None):
        self.dom = dom
        self.base_url = base_url
        self.realm = realm
        self.name = character_name
        if self.dom:
            self.parse_dom(self.dom)

    def parse_dom(self, dom):
        """TODO"""
        pass

    def get_gearscore(self):
        """Oh yeah!

        TODO!

        http://www.wowwiki.com/Gear_score"""
        stat_weights = {
            "Strength": 1.00,
            "Agility": 1.00,
            "Stamina": 2.00,
            "Intellect": 1.00,
            "Spirit": 1.00,
            "Arcane Resist": 1.00,
            "Fire Resist": 1.00,
            "Nature Resist": 1.00,
            "Frost Resist": 1.00,
            "Shadow Resist": 1.00,
            "Defense": 1.00,
            "Expertise": 1.00,
            "Block": 1.00,
            "Block Value": 0.65,
            "Dodge": 1.00,
            "Parry": 1.00,
            "Resilience": 1.00,
            "Armor Pen": 1.00,
            "Attack Power": 0.50,
            "Crit Rating": 1.00,
            "Ranged Crit": 1.00,
            "To Hit": 1.00,
            "Ranged To Hit": 1.00,
            "Haste": 1.00,
            "Damage Undead": 0.55,
            "Arcane Damage": 0.70,
            "Fire Damage": 0.70,
            "Frost Damage": 0.70,
            "Holy Damage": 0.70,
            "Nature Damage": 0.70,
            "Shadow Damage": 0.70,
            "Spell Penetration": 0.80,
            "Spell Power": 0.86,
            "Health Regen": 2.50,
            "Mana Regen": 2.50 
        }
        return 0


class Item(object):
    """TODO"""

    def __init__(self, id=None, dom=None, dom_tooltip=None):
        self.id = id
        self.dom = dom
        self.dom_tooltip = dom_tooltip

    def init_from_char_item_element(self, elem):
        # example of an element:
		#<item displayInfoId="64570" durability="100" gem0Id="41380" gem1Id="40141" gem2Id="0" gemIcon0="inv_jewelcrafting_shadowspirit_02" gemIcon1="inv_jewelcrafting_gem_40" icon="inv_helmet_158" id="51218" level="264" maxDurability="100" name="Sanctified Ymirjar Lord's Greathelm" permanentEnchantIcon="ability_warrior_swordandboard" permanentEnchantItemId="44150" permanentenchant="3818" pickUp="PickUpLargeChain" putDown="PutDownLArgeChain" randomPropertiesId="0" rarity="4" seed="0" slot="0"/>
        pass



def get_dom(reader):
    xml_str = reader.read()
    dom = xdm.parseString(xml_str)
    return dom

def write_str_to_file(str, filename):
    outfile = codecs.open(filename.encode(FILE_ENCODING), 'w')
    outfile.write(str)
    outfile.close()

def do_write_to_file(data, filename):
    outfile = codecs.open(filename.encode(FILE_ENCODING), 'w')
    outfile.write(data.read())
    outfile.close()

def open_url(url):
    opener = urllib2.build_opener()
    opener.addheaders = [('user-agent', USER_AGENT)]
    req = urllib2.Request(url)
    return opener.open(req)

def dump_url_to_file(url, filename, verbose, force):
    #TODO: check if file exists and only overwrite if 'force' is set
    if verbose:
        print "opening url '%s'..." % url,
    try:
        data = open_url(url)
    except:
        print "!"
        raise
    if verbose:
        print "done!"
    if verbose:
        print "writing '%s'..." % filename,
    do_write_to_file(data, filename)
    if verbose:
        print "done!"


def write_dom_to_xmlfile(dom, filename, dir="", pretty=False):
    try:
        path = dir + filename
        outfile = codecs.open(path.encode(FILE_ENCODING), 'w', FILE_ENCODING)
        if pretty:
            outfile.write(dom.toprettyxml())
        else:
            outfile.write(dom.toxml())
    finally:
        outfile.close()

def write_iteminfo(dom, item_id):
    filename = item_id + '.xml'
    write_dom_to_xmlfile(dom, filename, "items/")

def write_charactersheet(dom, character):
    filename = character + '.xml'
    write_dom_to_xmlfile(dom, filename, "chars/")

def write_guildinfo(dom, realm, guild):
    filename = realm + ' - ' + guild + '.xml'
    write_dom_to_xmlfile(dom, filename, "guild/")


def get_iteminfo_url(item_id, base_url):
    item_url = '%s%s?i=%s' % (
        base_url,
        'item-info.xml',
        item_id)
    return item_url

def get_itemtooltip_url(item_id, base_url):
    item_url = '%s%s?i=%s' % (
        base_url,
        'item-tooltip.xml',
        item_id)
    return item_url

def get_charactersheet_url(character, realm, base_url):
    character_url = '%s%s?r=%s&n=%s' % (
        base_url,
        'character-sheet.xml',
        realm.replace(' ', '+'),
        character.replace(' ', '+'))
    return character_url

def get_guildinfo_url(guild, realm, base_url):
    guild_url = '%s%s?r=%s&n=%s' % (
        base_url,
        "guild-info.xml",
        realm.replace(' ', '+'),
        guild.replace(' ', '+'))
    return guild_url


def do_dump(url, filename, verbose, force, write):
    if write:
        filename = "items/" + id + '.xml'
        dump_url_to_file(url, filename, verbose, force)
    else:
        data = open_url(url)
        sys.stdout.write(data.read())

def dump_item(id, base_url, verbose, force, write):
    url = get_iteminfo_url(id, base_url)
    filename = "items/" + id + '.xml'
    do_dump(url, filename, verbose, force, write)
    url2 = get_itemtooltip_url(id, base_url)
    filename2 = "items/" + id + '-tooltip.xml'
    do_dump(url2, filename2, verbose, force, write)

def dump_char(charname, realm, base_url, verbose, force, write):
    url = get_charactersheet_url(charname, realm, base_url)
    filename = "chars/" + charname + '.xml'
    do_dump(url, filename, verbose, force, write)

def dump_guild(realm, guild, base_url, verbose, force, write):
    url = get_guildinfo_url(guild, realm, base_url)
    filename = "guilds/" + realm + ' - ' + guild + '.xml'
    do_dump(url, filename, verbose, force, write)


def get_itemtooltip_dom(id, base_url):
    url = get_itemtooltip_url(id, base_url)
    reader = open_url(url)
    return get_dom(reader)

def get_item_dom(id, base_url):
    url = get_iteminfo_url(id, base_url)
    reader = open_url(url)
    return get_dom(reader)

def get_char_dom(charname, realm, base_url):
    url = get_charactersheet_url(charname, realm, base_url)
    reader = open_url(url)
    return get_dom(reader)

def get_guild_dom(realm, guild, base_url):
    url = get_guildinfo_url(guild, realm, base_url)
    reader = open_url(url)
    return get_dom(reader)


def usage():
    print __doc__


def _main(argv):
    flag_verbose = False
    flag_write = False
    flag_force = False
    class Flags: pass
    flags = Flags()
    flags.server_area = SERVER_AREA
    flags.realm = 'Trollbane'
    flags.guild = 'Emerge'
    flags.chars = []
    flags.items = []
    try:
        opts, args = getopt.getopt(argv, "hvwfr:g:c:i:", ["help", "verbose",
            "force", "realm", "guild", "char=", "itemid=", "eu", "us", ])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ('-v', '--verbose'):
            flag_verbose = True
            print "Verbose!"
        elif opt == '-w':
            flag_write = True
        elif opt in ('-f', '--force'):
            flag_force = True
        elif opt in ('-r', '--realm'):
            flags.realm = arg
        elif opt == '--eu':
            flags.server_area='EU'
        elif opt == '--us':
            flags.server_area='US'
        elif opt in ('-g', '--guild'):
            flags.guild = arg
        elif opt in ('-c', '--char'):
            flags.chars.append(arg)
        elif opt in ('-i', '--itemid'):
            flags.items.append(arg)

    flags.base_url = BASE_URLs[flags.server_area]

    # guild
    if not (flags.chars or flags.items):
        if flag_verbose:
            print "realm: '%s', guild: '%s'" % (flags.realm, flags.guild)
        dump_guild(flags.realm, flags.guild, flags.base_url, flag_verbose, flag_force, flag_write)

    # chars
    if flag_verbose:
        print "chars: '%s'" % (flags.chars or "<no chars!>")
    for char in flags.chars:
        dump_char(char, flags.realm, flags.base_url, flag_verbose, flag_force, flag_write)

    # items
    if flag_verbose:
        print "items: '%s'" % (flags.items or "<no items!>")
    for id in flags.items:
        dump_item(id, flags.base_url, flag_verbose, flag_force, flag_write)

if __name__ == "__main__":
    _main(sys.argv[1:])

