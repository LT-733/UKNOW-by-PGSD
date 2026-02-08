import csv

READFILENAME = "totalreparsed.csv"
OUTPUTFILENAME = "finalparsed.csv"
parseddata = []
knownunis = ['Wilfrid Laurier University', "Queen's University", 'University Of Ottawa', 'Trent University', 'University Of Waterloo', 'Laurentian University', 'Toronto Metropolitan University', 'Western University', 'Brock University', 'University Of Windsor', 'Ontario Tech University', 'Carleton University', 'Dalhousie University', 'York University', 'University of Guelph', 'University Of Alberta', 'Memorial University of Newfoundland', 'McGill University', 'University Of Toronto', 'McMaster University', 'University of British Columbia', 'Simon Fraser University', 'University of Toronto Mississauga', 'University of Toronto St. George', 'University Of New Brunswick', 'University Of Victoria', 'University Of Toronto Scarborough', 'Ontario College of Art and Design University', 'Nipissing University', 'Lakehead University', 'University Of Calgary', 'St. Francis Xavier University', 'Sheridan College', 'Humber College', 'Seneca Polytechnic', 'Langara College', 'Concordia University', 'George Brown Polytechnic']

aliases = {'Wilfrid Laurier University': 'Wilfrid Laurier University', 'Queens University': "Queen's University", "Queen'S University": "Queen's University", 'University Of Ottawa': 'University Of Ottawa', 'Trent University': 'Trent University', 'University Of Waterloo': 'University Of Waterloo', 'Laurentian University': 'Laurentian University', 'Toronto Metropolitan University': 'Toronto Metropolitan University', 'Western University': 'Western University', 'Ottawa University': "Queen's University", 'Brock University': 'Brock University', 'University Of Windsor': 'University Of Windsor', 'Ontario Tech University': 'Ontario Tech University', 'Carleton University': 'Carleton University', 'Dal': 'Dalhousie University', 'Dalhousie University': 'Dalhousie University', 'Dalhousie': "Queen's University", 'York University': 'York University', 'Guelph-Humber': 'University of Guelph', 'University Of Guelph': 'University of Guelph', 'University Of Guelph - Humber': "Queen's University", 'University Of Alberta': 'University Of Alberta', 'Waterloo Campus': "Queen's University", 'Memorial University': 'Memorial University of Newfoundland', 'Memorial University Of Newfoundland': 'Memorial University of Newfoundland', 'Mcgill University': 'McGill University', 'University Of Toronto': 'University Of Toronto', 'Gbc/Tmu (Collab) And York': "Queen's University", 'Mcmaster University': 'McMaster University', 'Ubc': 'University of British Columbia', 'University Of British Columbia': 'University of British Columbia', 'Simon Fraser University': 'Simon Fraser University', 'Trent Peterborough': "Queen's University", 'Trent University (Both Campuses)': "Queen's University", 'Tmu-Gbc': "Queen's University", 'Utm': 'University of Toronto Mississauga', 'University Of Toronto Mississauga': 'University of Toronto Mississauga', 'Simon Fraser University (Sfu)': "Queen's University", 'University Of Toronto St.G': 'University of Toronto St. George', 'University Of Toronto St. George': 'University of Toronto St. George', 'University Of New Brunswick': 'University Of New Brunswick', 'Western Ivey Aeo': "Queen's University", 'Ubcv': "Queen's University", 'University Of Victoria': 'University Of Victoria', 'Uoft St George': "Queen's University", 'University Of Toronto Scarborough': 'University Of Toronto Scarborough', 'Mississauga': "Queen's University", 'Uoft Mississauga': "Queen's University", 'University Of Toronto-Mississauga': "Queen's University", 'University Of Toronto - St. George': "Queen's University", 'Uoft Missisauga': "Queen's University", 'Mcgill': "Queen's University", 'Scarborough Campus': "Queen's University", 'Ocad University': 'Ontario College of Art and Design University', 'Ontario College Of Art And Design University': 'Ontario College of Art and Design University', 'Nipissing University': 'Nipissing University', 'Alberta': "Queen's University", 'Lakehead University': 'Lakehead University', 'University Of Calgary': 'University Of Calgary', 'St Francis Xavier University': 'St. Francis Xavier University', 'St. Francis Xavier University': 'St. Francis Xavier University', 'University Of Guelph-Humber': "Queen's University", 'Sheridan College': 'Sheridan College', 'Humber College': 'Humber College', 'Ubc!': "Queen's University", 'Seneca Gender Studies': 'Seneca Polytechnic', 'Seneca Polytechnic': 'Seneca Polytechnic', 'Langara In Bc!!!!': 'Langara College', 'Langara College': 'Langara College', 'Brock': "Queen's University", 'Carleton': "Queen's University", 'Concordia': 'Concordia University', 'Concordia University': 'Concordia University', 'George Brown': 'George Brown Polytechnic', 'George Brown Polytechnic': 'George Brown Polytechnic', 'Guelph': "Queen's University", 'Lakehead': "Queen's University", 'Laurentian': "Queen's University", 'Laurier': "Queen's University", 'Mcmaster': "Queen's University", 'Nipissing': "Queen's University", 'Ocad': "Queen's University", 'Ontario Tech': "Queen's University", "Queen'S": "Queen's University", 'Tmu': "Queen's University", 'Trent': "Queen's University", 'Uoft - Sg': "Queen's University", 'Uottawa': "Queen's University", 'Utsc': "Queen's University", 'Uvic': "Queen's University", 'Waterloo': "Queen's University", 'Western': "Queen's University", 'Western - Huron': "Queen's University", 'Windsor': "Queen's University", 'York': "Queen's University"}

knownmajors = [
    "Chemical Engineering",
    "Mechanical Engineering",
    "Electrical Engineering",
    "Computer Engineering",
    "Software Engineering",
    "Civil Engineering",
    "Biomedical Engineering",
    "Engineering Physics",
    "Computer Science",
    "Mathematics",
    "Statistics",
    "Physics",
    "Chemistry",
    "Biology",
    "Life Sciences",
    "Health Sciences",
    "Environmental Science",
    "Earth Science",
    "Business",
    "Business Administration",
    "Commerce",
    "Economics",
    "Psychology",
    "Sociology",
    "Political Science",
    "Data Science",
    "Kinesiology"
]

programaliases = {
    # Chemical Engineering
    "che": "Chemical Engineering",
    "cheme": "Chemical Engineering",
    "chem eng": "Chemical Engineering",
    "chemical eng": "Chemical Engineering",

    # Mechanical Engineering
    "me": "Mechanical Engineering",
    "meche": "Mechanical Engineering",
    "mech eng": "Mechanical Engineering",
    "mechanical eng": "Mechanical Engineering",

    # Electrical Engineering
    "ee": "Electrical Engineering",
    "elec eng": "Electrical Engineering",
    "electrical eng": "Electrical Engineering",

    # Computer Engineering
    "ce": "Computer Engineering",
    "comp eng": "Computer Engineering",
    "computer eng": "Computer Engineering",

    # Software Engineering
    "se": "Software Engineering",
    "soft eng": "Software Engineering",
    "software eng": "Software Engineering",

    # Civil Engineering
    "cive": "Civil Engineering",
    "civil eng": "Civil Engineering",

    # Biomedical Engineering
    "bme": "Biomedical Engineering",
    "biomed eng": "Biomedical Engineering",
    "biomedical eng": "Biomedical Engineering",

    # Engineering Physics
    "eng phys": "Engineering Physics",
    "engineering phys": "Engineering Physics",

    # Computer Science
    "cs": "Computer Science",
    "comp sci": "Computer Science",
    "computer sci": "Computer Science",
    "computing": "Computer Science",

    # Mathematics
    "math": "Mathematics",
    "applied math": "Mathematics",
    "pure math": "Mathematics",

    # Statistics
    "stats": "Statistics",
    "stat": "Statistics",

    # Physics
    "phys": "Physics",

    # Chemistry
    "chem": "Chemistry",

    # Biology / Life Sciences
    "bio": "Biology",
    "biol": "Biology",
    "life sci": "Life Sciences",
    "life sciences": "Life Sciences",

    # Health Sciences
    "health sci": "Health Sciences",
    "health sciences": "Health Sciences",

    # Environmental / Earth Sciences
    "env sci": "Environmental Science",
    "environmental sci": "Environmental Science",
    "earth sci": "Earth Science",

    # Business / Commerce
    "biz": "Business",
    "bba": "Business Administration",
    "business admin": "Business Administration",
    "commerce": "Commerce",
    "comm": "Commerce",

    # Economics
    "econ": "Economics",

    # Social Sciences
    "psych": "Psychology",
    "soci": "Sociology",
    "poli sci": "Political Science",
    "political sci": "Political Science",

    # Data / Interdisciplinary
    "data sci": "Data Science",
    "data science": "Data Science",

    # Kinesiology
    "kin": "Kinesiology",
    "kines": "Kinesiology"
}

with open(READFILENAME , mode = 'r') as raw:
    rawfile = csv.reader(raw)
    for lines in rawfile:
        #parseddata.append(lines)
        #print(lines)
        good = True
        try:
            if(lines[1] not in knownmajors and lines[1].lower() not in programaliases):
                print(lines[1] + " | " + lines[2])
                a = int(input("1 for keep program, 2 for assign to other program, 3 for rename program, 4 for throw out: "))
                if (a == 1):
                    programaliases[lines[1].lower()] = lines[1]
                    knownmajors.append(lines[1])
                elif (a == 2):
                    for i in range(len(knownmajors)):
                        print(str(i) + " | " + knownmajors[i])

                    index = int(input())
                    programaliases[lines[1].lower()] = knownmajors[1]
                elif (a == 3):
                    newname = input("new name: ")
                    programaliases[lines[1].lower()] = newname
                    programaliases[newname.title()] = newname
                    knownmajors.append(newname)
                elif (a == 4):
                    good = False
                else:
                    print(knownmajors)
                    print(programaliases)
            
            if(good):
                if lines[1] in knownmajors:
                    major_name = lines[1]
                else:
                    major_name = programaliases[lines[1].lower()]
                parseddata.append([lines[0], major_name, lines[2], lines[3], lines[4]])
        #except:
            #print(knownmajors)
            #print(programaliases)
            #print("what the f")
        except Exception as e:
            print(f"ERROR: {e}")
            print(f"Line causing issue: {lines}")
            print(f"Trying to access: '{lines[1].lower()}'")
            import traceback
            traceback.print_exc()
            
#print(knownmajors)
#print(programaliases)    

with open("known.csv", mode = 'w', newline = "", encoding="utf-8") as know:
    writer = csv.writer(know)

    for row in knownunis:
        writer.writerow([row])
        
print(parseddata)
with open(OUTPUTFILENAME, mode = 'w', newline = "", encoding="utf-8") as parsed:
    writer = csv.writer(parsed)

    for row in parseddata:
        writer.writerow(row)
