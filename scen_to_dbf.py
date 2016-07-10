#!/usr/bin/env python
import os.path
import sys
from collections import OrderedDict
from lxml.etree import tostring
from hearthstone.dbf import Dbf
from hearthstone.enums import Locale


try:
	from ScenarioDbRecord_pb2 import ScenarioDbRecord
except ImportError as e:
	sys.stderr.write("ERROR: %s\n" % (e))
	path = os.path.dirname(os.path.abspath(__file__))
	command = "protoc --python_out=%r %s" % (path, "ScenarioDbRecord.proto")
	sys.stderr.write("Try running `%s`\n" % (command))
	sys.exit(1)


class ScenarioProtoDBF(Dbf):
	name = "SCENARIO"
	source_fingerprint = None
	columns = OrderedDict([
		("ID", "Int"),
		("NOTE_DESC", "String"),
		("PLAYERS", "Int"),
		("PLAYER1_HERO_CARD_ID", "Int"),
		("PLAYER2_HERO_CARD_ID", "Int"),
		("IS_TUTORIAL", "Bool"),
		("IS_EXPERT", "Bool"),
		("IS_COOP", "Bool"),
		("ADVENTURE_ID", "Int"),
		("WING_ID", "Int"),
		("SORT_ORDER", "Int"),
		("MODE_ID", "Int"),
		("CLIENT_PLAYER2_HERO_CARD_ID", "Int"),
		("NAME", "LocString"),
		("SHORT_NAME", "LocString"),
		("DESCRIPTION", "LocString"),
		("OPPONENT_NAME", "LocString"),
		("COMPLETED_DESCRIPTION", "LocString"),
		("PLAYER1_DECK_ID", "Int"),
		("DECK_BUILDER_ID", "Int"),
		("DECK_RULESET_ID", "Int"),
		("TB_TEXTURE", "AssetPath"),
		("TB_TEXTURE_PHONE", "AssetPath"),
		("TB_TEXTURE_PHONE_OFFSET_Y", "Float"),
	])

	COLUMN_MAP = {
		"num_players": "PLAYERS",
		"adventure_mode_id": "MODE_ID",
		"tavern_brawl_texture": "TB_TEXTURE",
		"tavern_brawl_texture_phone": "TB_TEXTURE_PHONE",
		"tavern_brawl_texture_phone_offset": "TB_TEXTURE_PHONE_OFFSET_Y",
	}

	def __init__(self):
		self.records = []

	@classmethod
	def deserialize_locstrings(cls, strings):
		ret = {}
		for string in strings:
			ret[string.key] = {}
			for value in string.values:
				try:
					locale = Locale(value.locale).name
					ret[string.key][locale] = value.value
				except Exception:
					sys.stderr.write("WARNING: Invalid locale %r\n" % (value.locale))

		return ret

	def get_column_name(self, name):
		return self.COLUMN_MAP.get(name, name.upper())

	def load_proto(self, f):
		proto = ScenarioDbRecord()
		proto.ParseFromString(f.read())

		record = {
			"IS_TUTORIAL": False,
			"OPPONENT_NAME": None,
			"COMPLETED_DESCRIPTION": None,
			"PLAYER1_DECK_ID": None,
			"DECK_BUILDER_ID": None,
			"DECK_RULESET_ID": None,
		}

		for field in ScenarioDbRecord.DESCRIPTOR.fields:
			value = getattr(proto, field.name)
			if field.name == "strings":
				record.update(self.deserialize_locstrings(value))
				continue
			column = self.get_column_name(field.name)

			if column == "TB_TEXTURE_PHONE_OFFSET_Y":
				value = value.y

			record[column] = value

		self.records.append(record)


def main():
	dbf = ScenarioProtoDBF()

	for filename in sys.argv[1:]:
		with open(filename, "rb") as f:
			dbf.load_proto(f)

	xml = dbf._to_xml()
	ret = tostring(xml, encoding="utf-8", pretty_print=True, xml_declaration=True)
	print(ret.decode("utf-8"))


if __name__ == "__main__":
	main()
