import pandas as pd
import os
from .communicator import Communicator
from .settings import OUTPUT_PATH
from .error_codes import ERROR_CODES

class DataSaver:
    def __init__(self) -> None:
        self.outputFormat = Communicator.get_output_format()

    def save(self, datalist):
        """
        Save the scraped data in the specified format(s).
        This function can be called if any error occurs while scraping, or if scraping is done successfully.
        In both cases, we have to save the scraped data.
        """
        if len(datalist) > 0:
            Communicator.show_message("Saving the scraped data")

            dataFrame = pd.DataFrame(datalist)
            totalRecords = dataFrame.shape[0]

            searchQuery = Communicator.get_search_query()
            base_filename = f"{searchQuery} - GMS output"

            # Create the output directory if it does not exist
            if not os.path.exists(OUTPUT_PATH):
                os.makedirs(OUTPUT_PATH)

            def get_unique_filename(extension):
                """Generate a unique filename to avoid overwriting existing files."""
                filename = f"{base_filename}{extension}"
                joinedPath = os.path.join(OUTPUT_PATH, filename)
                index = 1
                while os.path.exists(joinedPath):
                    filename = f"{base_filename} ({index}){extension}"
                    joinedPath = os.path.join(OUTPUT_PATH, filename)
                    index += 1
                return joinedPath

            output_paths = []

            if self.outputFormat == "excel" or self.outputFormat == "excel+json":
                excel_path = get_unique_filename(".xlsx")
                dataFrame.to_excel(excel_path, index=False)
                output_paths.append(excel_path)

            if self.outputFormat == "csv":
                csv_path = get_unique_filename(".csv")
                dataFrame.to_csv(csv_path, index=False)
                output_paths.append(csv_path)

            if self.outputFormat == "json" or self.outputFormat == "excel+json":
                json_path = get_unique_filename(".json")
                dataFrame.to_json(json_path, indent=4, orient="records")
                output_paths.append(json_path)

            Communicator.show_message(
                f"Scraped data successfully saved! Total records saved: {totalRecords}.\nOutput files:\n" + "\n".join(output_paths)
            )
        else:
            Communicator.show_error_message(
                "Oops! Could not scrape the data because you did not scrape any record.",
                {ERROR_CODES['NO_RECORD_TO_SAVE']}
            )
