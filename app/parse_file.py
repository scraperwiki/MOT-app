def parse_file():
    Bigrecord = namedtuple("Bigrecord", "make model testresult year level1 level2 level3 modelcount")
    def make_record_level2(line):
        (make, model, testresult, year, level1, level2, level3, modelcount) = line
        return Bigrecord(make, model, testresult, year, level1, level2, level3, int(modelcount))

    with open("static/WholeData.csv") as fd1:
        records1 = list(csv.reader(fd1))
        records1 = records1[1:]
        records1 = [make_record_level2(r) for r in records1]

        data_dict = {}
        for r in records1:
            data_dict.setdefault(r.make, {}).setdefault(r.model, {}).setdefault(r.year, {}).setdefault(r.testresult, 
                []).append((r.level1, r.level2, r.level3, r.modelcount))

        data_dict_json = json.dumps(data_dict)

    with open("MakesAndModels.json", "w") as text_file:
        json.dump(data_dict_json, text_file, indent=2)