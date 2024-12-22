import express from "express";
import { Octokit } from "@octokit/rest";
import { GITHUB_TOKEN } from "./apikey.js";
import fs from "fs/promises"; // File system module for async/await operations

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
    regex = new RegExp(`function\\s+${functionName}\\s*\\(.*?\\)\\s*{[\\s\\S]*?}`, "g");
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

// Generate a call graph for a function
const generateCallGraph = (functionCode, functionName, fileName) => {
  if (!functionCode) return null;

  let callRegex;
  if (fileName.endsWith(".js") || fileName.endsWith(".ts")) {
    callRegex = /(\w+)\s*\(.*?\)/g;
  } else if (fileName.endsWith(".py")) {
    callRegex = /(\w+)\s*\(.*?\)/g;
  } else if (fileName.endsWith(".java") || fileName.endsWith(".cpp")) {
    callRegex = /(\w+)\s*\(.*?\)/g;
  } else {
    return null; // Unsupported language
  }

  const calls = [];
  let match;
  while ((match = callRegex.exec(functionCode)) !== null) {
    if (match[1] !== functionName) {
      calls.push(match[1]);
    }
  }

  return {
    function: functionName,
    calls,
  };
};

// Recursive function to explore directories and search for functions
const fetchSourceCode = async (owner, repo, path = "", sourceFile, functionFile, callGraphFile, functionName) => {
  const callGraphs = [];

  try {
    const content = await octokit.repos.getContent({ owner, repo, path });

    for (const item of content.data) {
      if (item.type === "dir" && item.name === "node_modules") {
        console.log(`Skipping directory: ${item.path}`);
        continue;
      }

      if (item.type === "file" && isSourceFile(item.name)) {
        console.log(`Processing file: ${item.path}`);
        const fileContent = await octokit.repos.getContent({
          owner,
          repo,
          path: item.path,
        });

        const decodedContent = Buffer.from(fileContent.data.content, "base64").toString("utf-8");

        const sourceOutput = `File: ${item.path}\n\n${decodedContent}\n\n===\n\n`;
        await fs.appendFile(sourceFile, sourceOutput, "utf-8");

        const functionCode = extractFunction(decodedContent, functionName, item.name);
        const functionOutput = `File: ${item.path}\n\n${functionCode || `Function '${functionName}' not found.`}\n\n===\n\n`;
        await fs.appendFile(functionFile, functionOutput, "utf-8");

        if (functionCode) {
          const callGraph = generateCallGraph(functionCode, functionName, item.name);
          if (callGraph) {
            callGraphs.push({
              file: item.path,
              callGraph,
            });
          }
        }
      } else if (item.type === "dir") {
        const subGraphs = await fetchSourceCode(
          owner,
          repo,
          item.path,
          sourceFile,
          functionFile,
          callGraphFile,
          functionName
        );
        callGraphs.push(...subGraphs);
      }
    }
  } catch (error) {
    console.error(`Error accessing ${path}:`, error.message);
  }

  return callGraphs;
};

// Set up Express server
const app = express();
const port = 3000;

app.use(express.json());

app.post("/fetch-source-code", async (req, res) => {
  const { owner, repo, functionName } = req.body;

  const sourceFile = `source_code_${repo}.txt`;
  const functionFile = `functions_${repo}.txt`;
  const callGraphFile = `call_graph_${repo}.json`;

  try {
    await fs.writeFile(sourceFile, `Source Code for Repository: ${repo}\n\n`, "utf-8");
    await fs.writeFile(functionFile, `Functions Matching '${functionName}' in Repository: ${repo}\n\n`, "utf-8");

    const callGraphs = await fetchSourceCode(
      owner,
      repo,
      "",
      sourceFile,
      functionFile,
      callGraphFile,
      functionName
    );

    await fs.writeFile(callGraphFile, JSON.stringify(callGraphs, null, 2), "utf-8");

    res.json({
      message: "Source code processed successfully",
      sourceFile,
      functionFile,
      callGraphFile,
    });
  } catch (error) {
    console.error("Error:", error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
