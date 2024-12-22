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

// Helper function to sanitize function names (remove parentheses)
const sanitizeFunctionName = (fnName) => fnName.replace(/\(\)$/, "");

// Fetch function details and return a structured JSON
const fetchFunctionDetails = async (owner, repo, functionName, callers, calls) => {
  const result = {
    function_code: null,
    callers_functions_code: {},
    calls_functions_code: {},
  };

  const fetchFunctionCode = async (fnName) => {
    let functionCode = null;

    const content = await octokit.repos.getContent({ owner, repo, path: "" });
    for (const item of content.data) {
      if (item.type === "file" && isSourceFile(item.name)) {
        const fileContent = await octokit.repos.getContent({
          owner,
          repo,
          path: item.path,
        });

        const decodedContent = Buffer.from(fileContent.data.content, "base64").toString("utf-8");
        functionCode = extractFunction(decodedContent, fnName, item.name);
        if (functionCode) break; // Stop when function is found
      }
    }
    return functionCode;
  };

  // Fetch the main function code
  result.function_code = await fetchFunctionCode(sanitizeFunctionName(functionName));

  // Fetch the caller function codes
  for (const caller of callers) {
    const sanitizedCaller = sanitizeFunctionName(caller);
    result.callers_functions_code[sanitizedCaller] = await fetchFunctionCode(sanitizedCaller);
  }

  // Fetch the called function codes
  for (const call of calls) {
    const sanitizedCall = sanitizeFunctionName(call);
    result.calls_functions_code[sanitizedCall] = await fetchFunctionCode(sanitizedCall);
  }

  return result;
};

// Set up Express server
const app = express();
const port = 3000;

app.use(express.json());

app.post("/fetch-function-details", async (req, res) => {
  const { owner, repo, functionName, callers, calls } = req.body;

  try {
    const result = await fetchFunctionDetails(owner, repo, functionName, callers, calls);

    // Write the result to a file
    const outputFileName = `function_details_${repo}.json`;
    await fs.writeFile(outputFileName, JSON.stringify(result, null, 2), "utf-8");

    // Respond with success
    res.json({
      message: "Function details fetched and written to file successfully.",
      outputFile: outputFileName,
      result,
    });
  } catch (error) {
    console.error("Error:", error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
