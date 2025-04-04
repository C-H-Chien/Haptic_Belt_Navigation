// // Last modified by Michael Vail, 2025.02.20
// // Handles the broader logic for an experimental session.

// using UnityEngine;
// using System.Collections;
// using System.Collections.Generic;
// using System.IO;
// using UnityEngine.UI;
// using System;
// using Unity.Netcode;

// public class SessionManager : NetworkBehaviour
// {
//     public TrialManager trialManager;
//     public DataManager dataManager;
//     public GameObject leftController, rightController, startHUD, waitingHUD, eventSystem;
//     public Text startInfoText;
//     private string subjectGroup, inputFileRoot, saveFilePath;
//     List<Trial> trials;
    
//     // Represents a single trial
//     [Serializable]
//     public class Trial
//     {
//         public int TrialNumber;
//         public int NumSubjects;
//         public float Angle;
//         public List<SubjectData> SubjectData;     // List of subjects involved in the trial
//         public bool IsCompleted;                  // Flag indicating whether the trial is completed
//     }

//     public void ProcessInputFile(string _subjectGroup)
//     {
//         if (!IsServer) return;

//         // Get input file root
//         subjectGroup = _subjectGroup; // "00"
//         inputFileRoot = $"Subj{subjectGroup}"; // "Subj00"

//         // If a save file exists, continue session from save point; otherwise, start new session from input file
//         saveFilePath = Path.Combine(Application.persistentDataPath, $"{inputFileRoot}_trialData.json");
//         trials = LoadSaveFile() ?? LoadNewFile();

//         // Continue with setup if trial list is initialized with save file or input file
//         if (trials != null) InitializeSession();
//     }

//     private List<Trial> LoadSaveFile()
//     {
//         if (!IsServer) return null;

//         try
//         {
//             string jsonData = File.ReadAllText(saveFilePath);
//             ListWrapper loadedData = JsonUtility.FromJson<ListWrapper>(jsonData);
//             return loadedData?.trials;
//         }
//         catch (FileNotFoundException) { return null; }
//     }

//     // Read trial data from the provided CSV file and parse it
//     private List<Trial> LoadNewFile()
//     {
//         if (!IsServer) return null;

//         // Attempt to load data from input file
//         TextAsset inputData = Resources.Load<TextAsset>(inputFileRoot);
//         if (inputData == null)
//         {
//             startInfoText.text = $"No input file found for subject group {subjectGroup}.";
//             return null;
//         }

//         // Initialize trials list and reader
//         trials = new();
//         StringReader reader = new(inputData.text);
//         reader.ReadLine(); // skip header
//         string line;

//         // Iterate through each line in the CSV file
//         while ((line = reader.ReadLine()) != null)
//         {
//             // Split the line by commas to extract values
//             string[] values = line.Split(",");

//             // Parse each value from the CSV line
//             int trialNumber = int.Parse(values[0]);
//             float angle = float.Parse(values[1]);
            
//             // Initialize new trial
//             Trial trial = new()
//             {
//                 TrialNumber = trialNumber,
//                 Angle = angle,
//                 SubjectData = new()
//             };

//             int numSubjects = 0;

//             // Create a new subject data struct for the remaining columns (2 per subject: start position and end position)
//             for (int i = 2; i < values.Length; i += 2)
//             {
//                 SubjectData subjectData = new()
//                 {
//                     StartPosition = values[i],
//                     EndPosition = values[i + 1]
//                 };
//                 trial.SubjectData.Add(subjectData);

//                 // Increment number of subjects
//                 numSubjects++;
//             }

//             trial.NumSubjects = numSubjects;
//             trials.Add(trial);
//         }

//         return trials;
//     }

//     // Session set-up process
//     private void InitializeSession()
//     {
//         if (!IsServer) return;

//         DestroyObjectsClientRpc(); // Remove unneeded game objects
//         dataManager.GetOutputPath(subjectGroup); // Initialize output path
//         StartCoroutine(RunTrials()); // Start session
//     }

//     // ClientRpc to notify the client to update or destroy non-networked objects
//     [ClientRpc]
//     private void DestroyObjectsClientRpc()
//     {
//         DestroyObjectsLocally();
//     }

//     // Destroy objects locally on the client
//     private void DestroyObjectsLocally()
//     {
//         Destroy(leftController);
//         Destroy(rightController);
//         startHUD.SetActive(false);
//         waitingHUD.SetActive(false);
//         eventSystem.SetActive(false);
//     }

//     // Run the trials
//     private IEnumerator RunTrials()
//     {
//         if (!IsServer) yield break;

//         // Run through each incomplete trial in the list
//         for (int i = 0; i < trials.Count; i++)
//         {
//             Trial currentTrial = trials[i];
            
//             if (!currentTrial.IsCompleted) {
//                 trialManager.isActive = true; // activate flag to indicate that a trial is now running
//                 trialManager.InitializeTrial(currentTrial); // Initialize and let TrialManager handle the trial logic
//                 yield return new WaitUntil(() => !trialManager.isActive); // Wait until the trial concludes (running flag is deactivated in TrialManager)
//                 yield return new WaitForSeconds(1f); // Wait briefly between trials
//                 currentTrial.IsCompleted = true; // Mark trial as complete
//                 SaveTrialData(); // save trial data after completion
//             }
//         }

//         // No more trials, end the session
//         trialManager.End();
//     }

//     // Serialize the trials list into JSON format and save session progress
//     public void SaveTrialData()
//     {
//         if (!IsServer) return;

//         string data = JsonUtility.ToJson(new ListWrapper { trials = trials }, true);
//         File.WriteAllText(saveFilePath, data);
//     }

//     // Wrapper class for serializing the list of trials, because JsonUtility requires it for some reason
//     [Serializable]
//     public class ListWrapper
//     {
//         public List<Trial> trials;  // List of trials
//     }
// }
