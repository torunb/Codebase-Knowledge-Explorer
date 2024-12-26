import fs from "fs"; // Standard fs module for createReadStream
import { createObjectCsvWriter } from "csv-writer";
import csv from "csv-parser";
import { Octokit } from "@octokit/rest";
import { GITHUB_TOKEN } from "./apikey.js";
import express from "express";


// Initialize Octokit with the user's token
const octokit = new Octokit({
  auth: GITHUB_TOKEN,
});

// Helper function to identify source code files
const isSourceFile = (fileName) => {
  const sourceExtensions = [".js", ".py", ".java", ".cpp", ".ts", ".go", ".rb", ".php"];
  return sourceExtensions.some((ext) => fileName.endsWith(ext));
};

// Helper function to extract functions using regex
const extractFunction = (content, functionName, fileName) => {
  let regex;
  if (fileName.endsWith(".js") || fileName.endsWith(".ts")) {
    regex = new RegExp(
      `(function\\s+${functionName}\\s*\\(.*?\\)\\s*{[\\s\\S]*?})|(${functionName}\\s*:\\s*function\\s*\\(.*?\\)\\s*{[\\s\\S]*?})|(${functionName}\\s*=\\s*\\(.*?\\)\\s*=>\\s*{[\\s\\S]*?})`,
      "g"
    );
  } else if (fileName.endsWith(".py")) {
    regex = new RegExp(`def\\s+${functionName}\\s*\\(.*?\\):[\\s\\S]*?(?=\\n\\S|$)`, "g");
  } else if (fileName.endsWith(".java") || fileName.endsWith(".cpp")) {
    regex = new RegExp(`${functionName}\\s*\\(.*?\\)\\s*\\{[\\s\\S]*?\\}`, "g");
  } else {
    return null; // Unsupported language
  }

  const matches = content.match(regex);
  return matches ? matches.join("\n\n") : null;
};

// Fetch function code from a repository
const fetchFunctionCode = async (owner, repo, functionName) => {
  let functionCode = null;

  try {
    const content = await octokit.repos.getContent({ owner, repo, path: "" });
    for (const item of content.data) {
      if (item.type === "file" && isSourceFile(item.name)) {
        const fileContent = await octokit.repos.getContent({
          owner,
          repo,
          path: item.path,
        });

        const decodedContent = Buffer.from(fileContent.data.content, "base64").toString("utf-8");
        functionCode = extractFunction(decodedContent, functionName, item.name);
        if (functionCode) break; // Stop when function is found
      }
    }
  } catch (error) {
    console.error(`Error fetching function ${functionName}:`, error.message);
  }

  return functionCode;
};

// Process CSV file to fetch function codes and write to a new column
const processCsv = async (csvFilePath, owner, repo, outputCsvFilePath) => {
  const rows = []; // To hold the updated rows
  const functionQueue = []; // To handle asynchronous processing

  return new Promise((resolve, reject) => {
    fs.createReadStream(csvFilePath)
      .pipe(csv())
      .on("data", (row) => {
        functionQueue.push(
          (async () => {
            const functionName = row.CODE;
            const functionCode = await fetchFunctionCode(owner, repo, functionName);
            rows.push({
              CODE: functionName,
              "ORIGINAL CODE": functionCode || "Not Found", // Add fetched code or "Not Found"
            });
          })()
        );
      })
      .on("end", async () => {
        // Wait for all async operations to complete
        await Promise.all(functionQueue);

        // Write updated rows to a new CSV
        const csvWriter = createObjectCsvWriter({
          path: outputCsvFilePath,
          header: [
            { id: "CODE", title: "CODE" },
            { id: "ORIGINAL CODE", title: "ORIGINAL CODE" },
          ],
        });

        await csvWriter.writeRecords(rows);
        resolve(`CSV processing complete. Output written to ${outputCsvFilePath}`);
      })
      .on("error", (error) => reject(error));
  });
};

// Example usage with Express
const app = express();
const port = 3000;

app.use(express.json());

app.post("/process-csv", async (req, res) => {
  const { csvFilePath, owner, repo, outputCsvFilePath } = req.body;

  try {
    const message = await processCsv(csvFilePath, owner, repo, outputCsvFilePath);
    res.json({ message });
  } catch (error) {
    console.error("Error processing CSV:", error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
