#!/usr/bin/env python
import os.path
import sys
from enum import IntEnum
from xml.dom import minidom
from xml.etree import ElementTree


try:
	from ScenarioDbRecord_pb2 import ScenarioDbRecord
except ImportError as e:
	sys.stderr.write("ERROR: %s\n" % (e))
	path = os.path.dirname(os.path.abspath(__file__))
	command = "protoc --python_out=%r %s" % (path, "ScenarioDbRecord.proto")
	sys.stderr.write("Try running `%s`\n" % (command))
	sys.exit(1)


class Locale(IntEnum):
	UNKNOWN = -1
	enUS = 0
	enGB = 1
	frFR = 2
	deDE = 3
	koKR = 4
	esES = 5
	esMX = 6
	ruRU = 7
	zhTW = 8
	zhCN = 9
	itIT = 10
	ptBR = 11
	plPL = 12
	ptPT = 13
	jaJP = 14
	thTH = 15


column_map = {
	"num_players": "PLAYERS",
	"adventure_mode_id": "MODE_ID",
}

column_names = [
	"ID", "NOTE_DESC", "PLAYERS", "PLAYER1_HERO_CARD_ID", "PLAYER2_HERO_CARD_ID",
	"IS_TUTORIAL", "IS_EXPERT", "ADVENTURE_ID", "MODE_ID", "NAME", "SHORT_NAME",
	"DESCRIPTION", "COMPLETED_DESCRIPTION", "WING_ID", "SORT_ORDER",
	"CLIENT_PLAYER2_HERO_CARD_ID", "OPPONENT_NAME", "TAVERN_BRAWL_TEXTURE",
	"TAVERN_BRAWL_TEXTURE_PHONE", "TAVERN_BRAWL_TEXTURE_PHONE_OFFSET_X",
	"TAVERN_BRAWL_TEXTURE_PHONE_OFFSET_Y",
]


def get_column_name(field_name):
	return column_map.get(field_name, field_name.upper())


def pretty_xml(xml):
	ret = ElementTree.tostring(xml)
	ret = minidom.parseString(ret).toprettyxml(indent="\t")
	return "\n".join(line for line in ret.split("\n") if line.strip())


def proto_to_xml(record):
	xml_record = ElementTree.Element("Record")
	values = decompile_proto(record)
	for field_name in column_names:
		if field_name == "IS_TUTORIAL":
			value = False
		elif field_name in ("COMPLETED_DESCRIPTION", "OPPONENT_NAME"):
			value = ""
		else:
			value = values[field_name]
		e = ElementTree.Element("Field")
		e.attrib["column"] = field_name
		if isinstance(value, dict):
			# Turn LocStrings into a sub-tree of locale elements
			for locale in Locale:
				if locale.name not in value:
					continue
				locale_elem = ElementTree.Element(locale.name)
				locale_elem.text = value[locale.name]
				e.append(locale_elem)
		else:
			e.text = str(value)
		xml_record.append(e)

	return xml_record


def decompile_proto(record):
	values = {}
	for string in record.strings:
		strings = {}
		for value in string.values:
			try:
				locale = Locale(value.locale).name
				strings[locale] = value.value
			except Exception:
				sys.stderr.write("WARNING: Invalid locale %r\n" % (value.locale))
		values[string.key] = strings

	for field in ScenarioDbRecord.DESCRIPTOR.fields:
		field_name = get_column_name(field.name)
		value = getattr(record, field.name)
		if field.name == "tavern_brawl_texture_phone_offset":
			values[field_name + "_X"] = value.x
			values[field_name + "_Y"] = value.y
		else:
			values[field_name] = str(value)
	return values


def main():
	root = ElementTree.Element("Dbf")

	for filename in sys.argv[1:]:
		with open(filename, "rb") as f:
			record = ScenarioDbRecord()
			record.ParseFromString(f.read())
			xml_record = proto_to_xml(record)
			root.append(xml_record)

	print(pretty_xml(root))


if __name__ == "__main__":
	main()
