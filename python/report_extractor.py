

'''

This script scrapes the bigfoot field researchers organization's website (https://www.bfro.net/GDB/) for reports of bigfoot sightings.
Assume that the current directory is bigfoot_sightings, which means this script should be run using something like this: python3 ./python/report_extractor.py
This script takes the report_links.json file generated by the bigfoot_downloader.py file. 

'''





# Import libraries ---------------------------------------------------------------------------------------------------

import requests, bs4, re, json, time, secrets, os, unicodedata



# check current directory---------------------------------------------------------------------------------------------------

# check current directory
current_folder = os.path.split(os.getcwd())[-1]


# assume that the most likely error is that the script is being run inside the python folder
# instead of one folder up
if current_folder != "bigfoot_sightings":
	os.chdir("..")


# make all other weird current directories return an error
current_folder = os.path.split(os.getcwd())[-1]

if current_folder != "bigfoot_sightings":
	raise Exception("Not sure where you're trying to run this script from. Please manually edit your file paths and then delete this exception")

# define file paths ---------------------------------------------------------------------------------------------------
report_links_path = './data/raw_data/report_links.json'
output_file = './data/raw_data/all_sightings.json'

# load data ---------------------------------------------------------------------------------------------------------

# open json file
f = open(report_links_path)
 
# load json into dictionary
just_report_links = json.load(f)


# Define functions ---------------------------------------------------------------------------------------------------------


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



	# assume the report date is always the first field
	report["report_date"] = soup.select("span.field")[0].getText()


	# get rid of stupid encoding issues: https://stackoverflow.com/questions/10993612/how-to-remove-xa0-from-string-in-python
	report["report_date"] = unicodedata.normalize("NFKD", report["report_date"] ).strip()


	# find all the elements with a field class inside of a <p> element
	field_elems = soup.select("p .field")

	# extract all the keys and values associated with each field
	for i in range(len(field_elems)):

		text = field_elems[i].parent.getText().split(":")[1:]
		text = "".join(text).strip()

		report[field_elems[i].parent.getText().split(":")[0]] = text



	# add the url as the last field
	report["url"] = report_url




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






