
# Import libraries ---------------------------------------------------------------------------------------------------

import requests, bs4, re, json, time, secrets


# Define constants --------------------------------------------------------------------------------------------------------

# this is the url of the main page of the sightings database
# all the reports are sublinks or sub-sublinks off of this page
landing_page = "https://www.bfro.net/GDB/"


# output file
# this is the json file where we'll write the reports to
output_file = "all_sightings.json"

# Define functions ---------------------------------------------------------------------------------------------------------


 
# Opening JSON file
f = open('report_links.json')
 
# returns JSON object as 
# a dictionary
just_report_links = json.load(f)




# function to extract data from each report page 
def pull_report(report_url):


	# create an empty dictionary
	report = {}

    # download html for report page
	res = requests.get(report_url)

	# parse html 
	soup = bs4.BeautifulSoup(res.text, "html.parser")


	# add additional fields that aren't contained in a .field class

	# extract numbers from report numbers field
	report["report_no"] = ''.join([c if c.isdigit() else '' for c in soup.select(".reportheader")[0].getText()])

	# extract report classification
	classification = soup.select(".reportclassification")[0].getText()

	#get just the letter
	report_letter = re.compile(" [A-C]").findall(classification)

	#remove extra white space and add to dictionary
	report["classification"] = ''.join(report_letter).strip()


	# not the best strategy, but we'll assume that this field
	# will always be the second field, so we'll hardcode it in
	report["summary"] = soup.select("span.field")[1].getText()


	# find all the elements with a field class inside of a <p> element
	field_elems = soup.select("p .field")

	# extract all the keys and values associated with each field
	for i in range(len(field_elems)):

		text = field_elems[i].parent.getText().split(":")[1:]
		text = "".join(text).strip()

		report[field_elems[i].parent.getText().split(":")[0]] = text




	return(report)












# create empty dictionary
all_sightings_dict = {}

# loop through all the links and add to the dictionary

for i in range(len(just_report_links)):


	# print periodic status updates
	if i % 100 == 0:
		print(f"Finished report number {i}")


	# pause for a random amount of time between 0-2 seconds
	time.sleep(secrets.randbelow(200) / 100)


	# pull all the data from the reports and write to file
	all_sightings_dict[i] = pull_report(just_report_links[i])


# write the dictionary to a json file
with open(output_file, "w") as f: 
    json.dump(all_sightings_dict, f)




