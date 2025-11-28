from utils import search_oportunities
import csv

if __name__ == "__main__":
    keywords = "LLM"
    df_jobs = search_oportunities(keywords =keywords)
    df_jobs.to_csv(r"{}.csv".format(keywords), quoting=csv.QUOTE_NONNUMERIC, sep=";" ,index=False)
    print("CSV file created: {}.csv".format(keywords))