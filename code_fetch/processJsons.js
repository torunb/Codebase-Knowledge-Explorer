import fs from 'fs/promises';
import path from 'path';
import axios from 'axios';

const testJsonsFolder = '/Users/borantorun/Documents/GitHub/Codebase-Knowledge-Explorer/test_jsons'; // Path to the folder with test JSON files
const serverUrl = 'http://localhost:3000/fetch-function-details'; // Endpoint of your server
const progressFile = '/Users/borantorun/Documents/GitHub/Codebase-Knowledge-Explorer/last_processed.json'; // File to store the last processed file

const saveProgress = async (fileName) => {
  try {
    await fs.writeFile(progressFile, JSON.stringify({ lastProcessed: fileName }, null, 2), 'utf-8');
    console.log(`Progress saved: ${fileName}`);
  } catch (error) {
    console.error('Error saving progress:', error.message);
  }
};

const getLastProcessed = async () => {
  try {
    const data = await fs.readFile(progressFile, 'utf-8');
    const { lastProcessed } = JSON.parse(data);
    return lastProcessed || null;
  } catch {
    return null; // Default to null if the file doesn't exist or can't be read
  }
};

const processFilesSequentially = async () => {
  try {
    // Read the directory and get all JSON files
    const files = await fs.readdir(testJsonsFolder);
    const jsonFiles = files.filter((file) => file.endsWith('.json'));

    // Get the last processed file
    const lastProcessed = await getLastProcessed();
    const startIndex = lastProcessed ? jsonFiles.indexOf(lastProcessed) + 1 : 0;
    const filesToProcess = jsonFiles.slice(startIndex);

    for (const file of filesToProcess) {
      const filePath = path.join(testJsonsFolder, file);

      // Read the JSON file
      const fileContent = await fs.readFile(filePath, 'utf-8');
      const requestData = JSON.parse(fileContent);

      console.log(`Processing file: ${file}`);

      try {
        // Send the POST request with a timeout
        const response = await axios.post(serverUrl, requestData, { timeout: 15000 }); // 10s timeout
        console.log(`Response for ${file}:`, response.data);

        // Save progress
        await saveProgress(file);
      } catch (error) {
        console.error(`Error or timeout processing ${file}:`, error.message);
        console.error('Stopping further processing to retry later.');
        break; // Stop processing further files
      }
    }

    console.log("Processing completed.");
  } catch (error) {
    console.error("Error reading files or processing requests:", error.message);
  }
};

// Run the sequential processing
processFilesSequentially();
