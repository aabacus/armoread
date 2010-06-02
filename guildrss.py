#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Make an OPML file from a guild roster, read from wow armory.

Parses a XML file containing a guild to make a OPML file outlining based on
the guild ranks.

TODO
----
* Make it read rank mapping from argv. For example
    $ guildrss -m "0135 6 8 279"
    ie, map ranks 0, 1, 3 and 5 to the same outline (group) and
    ranks 2, 7 and 9 into another group and skip rank 4 (not specified).

* Support flags to chose what to subscribe to (instance, loot, achievs...)

Future plans
------------
Look into supporting other output formats than OPML
    (http://en.wikipedia.org/wiki/OPML):
    OML, XOXO, XBEL
"""

import sys
import getopt
import xml.dom.minidom as xdm
import armoread

#<?xml version="1.0" encoding="UTF-8"?>
#<opml version="1.0">
#    <head>
#        <title>ron-e subscriptions in Google Reader</title>
#    </head>
#    <body>
#        <outline title="Raid Member" text="Raid Member">
#            <outline text="WoW Feed for Aabacus@Trollbane"
#                title="WoW Feed for Aabacus@Trollbane"
#                type="rss"
#                xmlUrl="http://eu.wowarmory.com/character-feed.atom?r=Trollbane&amp;cn=Aabacus"
#                htmlUrl="http://eu.wowarmory.com/character-feed.atom?r=Trollbane&amp;cn=Aabacus"/>
#           [...]

#        <character achPoints="105" classId="1" genderId="1" level="80" name="Aabacus" raceId="4" rank="1" url="r=Trollbane&amp;cn=Aabacus"/>

def add_group_outlines(group_names, body, doc):
    for gn in group_names:
        outline = doc.createElement("outline")
        body.appendChild(outline)
        outline.setAttribute("title", "%s" % gn)
        outline.setAttribute("text", "%s" % gn)
        group_names[gn]["outline"] = outline

def add_char(rank_mappings, character, doc, realm_name):
    character_rank = character.getAttribute("rank")
    character_name = character.getAttribute("name")
    outline = rank_mappings[character_rank]["outline"]
    char = doc.createElement("outline")
    outline.appendChild(char)
    char.setAttribute("text", "WoW Feed for %s@%s" % (character_name, realm_name))
    char.setAttribute("title", "WoW Feed for %s@%s" % (character_name, realm_name))
    char.setAttribute("type", "rss")
    char.setAttribute("xmlUrl",
            "http://eu.wowarmory.com/character-feed.atom?r=%s&cn=%s" %
            (realm_name, character_name))
    char.setAttribute("htmlUrl",
            "http://eu.wowarmory.com/character-feed.atom?r=%s&cn=%s" %
            (realm_name, character_name))

def get_opml_doc(rank_mappings, group_names, realm, guild, base_url):
    """return a xml.dom.minidom document

    rank_mappings -- {"0": GROUP, "1":...}
    group_names -- {GROUP_NAME: GROUP, ...}
    where
        GROUP -- {"name": GROUP_NAME, "outline": OUTLINE, "elems":[]}
        GROUP_NAME -- is the concatenation of each rank name in that group.
        OUTLINE -- is an outline element
    """
    doc = xdm.Document()
    opml = doc.createElement("opml")
    opml.setAttribute("version", "1.0")
    doc.appendChild(opml)
    head = doc.createElement("head")
    opml.appendChild(head)
    title = doc.createElement("title")
    head.appendChild(title)
    title_text = doc.createTextNode("%s@%s" % (guild, realm))
    title.appendChild(title_text)
    body = doc.createElement("body")
    opml.appendChild(body)

    add_group_outlines(group_names, body, doc)

    guild_dom = armoread.get_guild_dom(realm, guild, base_url)
    for char in guild_dom.getElementsByTagName("character"):
        add_char(rank_mappings, char, doc, realm)

    return doc


def usage():
    print __doc__

def parse_ranks(arg):
    rank_names = {0: "Guild Master", 1: "Officer", 2: "Officers alt", 3: "Raid Leader", 4: "?Loot Council?", 5: "Raid Member", 6: "Trial", 7: "Alts", 8: "Social", 9: "Social Alts", }

    # split string to rank groups, ie "013 2 4" => ["013", "2", "4"]
    _str_groups = arg.split(" ")
    # create an empty elements' list for each group and tie them together in
    # a dict with their ranks names combined to a string:
    # => [{name:"013", elems:[]}, {name:"2", elems:[]}, {name:"4", elems:[]}]
#    _groups = [(str_grp, {"name": ", ".join([rank_names[int(rank)] for rank in str_grp]), "elems": []}) for str_grp in _str_groups]
    _groups = []
    res_group_names = {}
    for str_grp in _str_groups:
        ranks = [rank_names[int(rank)] for rank in str_grp]
        group_name = ", ".join(ranks)
        group = {"name": group_name, "elems": []}
        _groups.append((str_grp, group))
        res_group_names[group["name"]] = group

    # make a dict with each rank in the same group point to the same value
    res_ranks = {}
    for ranks, group in _groups:
        for r in ranks:
            res_ranks[r] = group

    return res_ranks, res_group_names

def _main(argv):
    flag_verbose = False
    flag_write = False
    flag_force = False
    class Flags: pass
    flags = Flags()
    flags.server_area = armoread.SERVER_AREA
    flags.realm = 'Trollbane'
    flags.guild = 'Emerge'
    flags.rank_mappings = {}
    flags.group_names = {}
    try:
        opts, args = getopt.getopt(argv, "hvm:rgwf", ["help", "verbose",
            "map", "realm", "guild", "char=", "itemid=", "eu", "us", "force"])
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
        elif opt in ('-m', '--map'):
            flags.rank_mappings, flags.group_names = parse_ranks(arg)
        elif opt in ('-r', '--realm'):
            flags.realm = arg
        elif opt == '--eu':
            flags.server_area='EU'
        elif opt == '--us':
            flags.server_area='US'
        elif opt in ('-g', '--guild'):
            flags.guild = arg
        elif opt == '-w':
            flag_write = True
        elif opt in ('-f', '--force'):
            flag_force = True

    flags.base_url = armoread.BASE_URLs[flags.server_area]

    opml_doc = get_opml_doc(flags.rank_mappings, flags.group_names, flags.realm, flags.guild, flags.base_url)
    pretty_xml = opml_doc.toprettyxml(encoding="utf-8", indent="    ")
    filename = "opml-" + flags.guild + "-" + flags.realm + ".xml"
    armoread.write_str_to_file(pretty_xml, filename)


if __name__ == "__main__":
    _main(sys.argv[1:])

