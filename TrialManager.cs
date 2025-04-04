// // Last modified by Michael Vail, 2025.02.28
// // Handles the setup, execution, and data collection of an individual trial in an experiment.

// using UnityEngine;
// using System.Collections.Generic;
// using System.Text;
// using System.Collections;
// using System.Linq;

// public class TrialManager : NetworkBehaviour
// {
//     // References to other systems that the trial manager interacts with
//     public SessionManager sessionManager;
//     public DataManager dataManager;

//     // Internal variables for managing the trial's state and setup
//     public bool isActive = false; // Flag to indicate whether the trial is currently active
//     public List<GameObject> homePolePrefabs, goalPolePrefabs;
//     public int numPolePositions; // Number of positions around the area circle that a pole can spawn

//     private System.Diagnostics.Stopwatch stopwatch;
//     private StringBuilder dataBuilder;
//     private AudioSource audioSource;
//     private AudioClip begin, end;
//     private readonly int targetFrameRate = 72;
//     private int trial, numSubjects;
//     private float angle;
//     private string stage, dataBuffer;
//     private bool headerInitialized = false;
//     private float[] subjectTimers;
//     private bool[] subjectReady;
//     private List<SubjectData> subjectData;
//     private Dictionary<string, Vector3> polePositions;
//     private List<GameObject> homes, goals;
//     private IReadOnlyList<NetworkClient> clients;

//     // Constants for various parameters of the experimental space
//     private const float PoleTriggerRadius = 0.3f; // Radius within which the participant must be to interact with the home pole
//     private const float OrientTime = 3f; // Time the participant needs to orient onto the pole
//     private const double DimensionX = 9; // The width of the experimental space
//     private const double DimensionZ = 11; // The depth of the experimental space

//     // Initialization logic
//     private void Start()
//     {
//         Application.targetFrameRate = targetFrameRate; // Set frame rate

//         // Initialize audio source if it's not already present
//         if (!Camera.main.TryGetComponent(out audioSource))
//         {
//             audioSource = Camera.main.gameObject.AddComponent<AudioSource>();
//             audioSource.volume = 0.5f;
//             audioSource.playOnAwake = false;
//         }

//         // Load the beginning and ending audio clips
//         begin = Resources.Load<AudioClip>("Begin");
//         end = Resources.Load<AudioClip>("End");

//         // Calculate circle inside room bounds and place possible pole positions along the perimeter, evenly spaced given n positions
//         polePositions = CalculatePolePositions();
//     }

//     // Initializes a new trial by setting up trial data and resetting trial state
//     public void InitializeTrial(SessionManager.Trial currentTrial)
//     {
//         if (!IsServer) return;

//         trial = currentTrial.TrialNumber;
//         numSubjects = currentTrial.NumSubjects;
//         angle = currentTrial.Angle;
//         subjectData = currentTrial.SubjectData;
//         ResetTrial();
//     }

//     // Resets variables and sets up objects for the next trial
//     private void ResetTrial()
//     {
//         if (!IsServer) return;

//         stage = "";
//         dataBuffer = "";
//         stopwatch = new();
//         dataBuilder = new();
//         homes = new();
//         goals = new();
//         subjectTimers = new float[numSubjects];
//         subjectReady = new bool[numSubjects];

//         // Initialize timers and ready indicators
//         for (int i = 0; i < numSubjects; i++)
//         {
//             subjectTimers[i] = 0f;
//             subjectReady[i] = false;
//         }

//         // Initialize data buffer with headers
//         if (!headerInitialized) InitializeHeader();

//         // Spawn poles and enter "begin" stage
//         SpawnPoles();
//         stage = "begin";
//     }

//     private void FixedUpdate()
//     {
//         if (!IsServer) return;

//         clients = NetworkManager.Singleton.ConnectedClientsList;
        
//         if (stage == "record") CollectData();
//         else if (stage == "begin")
//         {
//             CheckSubjectsReady();
//             if (subjectReady.All(ready => ready)) StartTrial();
//         }
//     }

//     private void StartTrial()
//     {
//         if (!IsServer) return;

//         DestroyPoles(homes);
//         StartCoroutine(RecordTrial());
//     }

//     // Handles the execution of a trial, including data collection
//     private IEnumerator RecordTrial()
//     {
//         if (!IsServer) yield break;

//         stopwatch.Start(); // start stopwatch
//         PlayAudioClientRpc("begin"); // Play the "begin" audio clip
//         stage = "record"; // Start the recording stage

//         yield return new WaitUntil(AllSubjectsReachedGoals); // Wait until all subjects reach their goal poles
        
//         // Clean up after trial concludes and write data to file
//         stage = "";
//         DestroyPoles(goals);
//         stopwatch.Stop();
//         dataManager.WriteToFile(dataBuffer);
//         isActive = false;
//     }




//     // HELPER FUNCTIONS

//     private Dictionary<string, Vector3> CalculatePolePositions()
//     {
//         Dictionary<string, Vector3> polePositions = new();
//         float radius = Mathf.Min((float)(DimensionX - 1), (float)(DimensionZ - 1)) / 2;
//         float angleStep = 2 * Mathf.PI / numPolePositions;

//         for (int i = 0; i < numPolePositions; i++)
//         {
//             // Assuming center is (0, 0)
//             float angle = i * angleStep;
//             float x = radius * Mathf.Cos(angle);
//             float z = radius * Mathf.Sin(angle);
//             polePositions.Add(((char)('A' + i)).ToString(), new Vector3(x, 1, z));
//         }

//         return polePositions;
//     }

//     private void InitializeHeader()
//     {
//         // Global or host info
//         dataBuilder.Append("trial,numSubjects,angle,timeStamp,dataCollectionFrequency,FPS");

//         // Per subject info
//         for (int i = 0; i < numSubjects; i++)
//         {
//             char subjectChar = (char)('A' + i);
//             dataBuilder.AppendFormat(",subj{0}_X,subj{0}_Y,subj{0}_Z,subj{0}_pitch,subj{0}_yaw,subj{0}_roll", subjectChar);
//         }

//         dataBuilder.AppendLine();
//         dataBuffer = dataBuilder.ToString();
//         headerInitialized = true;
//     }
    
//     private void SpawnPoles()
//     {
//         if (!IsServer) return;

//         for (int i = 0; i < numSubjects; i++)
//         {
//             var home = Instantiate(homePolePrefabs[i], polePositions[subjectData[i].StartPosition], Quaternion.identity);
//             homes.Add(home);
//             var homeNetworkObject = home.GetComponent<NetworkObject>();
//             homeNetworkObject.Spawn();
//             SpawnPoleClientRpc(homeNetworkObject.NetworkObjectId);

//             var goal = Instantiate(goalPolePrefabs[i], polePositions[subjectData[i].EndPosition], Quaternion.identity);
//             goals.Add(goal);
//             var goalNetworkObject = goal.GetComponent<NetworkObject>();
//             goalNetworkObject.Spawn();
//             SpawnPoleClientRpc(goalNetworkObject.NetworkObjectId);
//         }
//     }

//     [ClientRpc]
//     private void SpawnPoleClientRpc(ulong networkObjectId)
//     {
//         if (NetworkManager.Singleton.SpawnManager.SpawnedObjects.TryGetValue(networkObjectId, out var _))
//             Debug.Log($"Successfully spawned pole with NetworkObjectId: {networkObjectId}");
//         else
//             Debug.LogError($"Failed to spawn pole on client. NetworkObjectId: {networkObjectId} not found.");
//     }

//     private void CheckSubjectsReady()
//     {
//         if (!IsServer) return;

//         for (int i = 0; i < numSubjects; i++)
//         {
//             Vector3 subjectPosition = clients[i].PlayerObject.transform.position;

//             if (IsInRadius(subjectPosition, homes[i].transform.position, PoleTriggerRadius))
//             {
//                 subjectTimers[i] += Time.fixedDeltaTime; // subject on home pole, increment time
//                 if (subjectTimers[i] > OrientTime) subjectReady[i] = true; // if subject has been on home pole for long enough, they are ready
//             }
//             else
//             {
//                 // Subject not on home pole, reset timer to 0 and indicate not ready
//                 subjectTimers[i] = 0f;
//                 subjectReady[i] = false;
//             }
//         }
//     }

//     private void DestroyPoles(List<GameObject> poles)
//     {
//         if (!IsServer) return;

//         List<ulong> poleNetworkObjectIds = poles.Select(pole => pole.GetComponent<NetworkObject>().NetworkObjectId).ToList();
//         NetworkObjectIdList poleNetworkObjectIdList = new() { NetworkObjectIds = poleNetworkObjectIds };
//         DestroyPolesClientRpc(poleNetworkObjectIdList);

//         foreach (var pole in poles) Destroy(pole);
//         poles.Clear();
//     }

//     [ClientRpc]
//     private void DestroyPolesClientRpc(NetworkObjectIdList poleNetworkObjectIdList)
//     {
//         foreach (var networkObjectId in poleNetworkObjectIdList.NetworkObjectIds)
//             if (NetworkManager.Singleton.SpawnManager.SpawnedObjects.TryGetValue(networkObjectId, out var networkObject)) networkObject.Despawn();
//     }

//     private bool AllSubjectsReachedGoals()
//     {
//         if (!IsServer) return false;
            
//         return clients.Select((client, index) => IsInRadius(client.PlayerObject.transform.position, goals[index].transform.position, PoleTriggerRadius))
//             .All(reachedGoal => reachedGoal);
//     }

//     // Gathers data about the trial's progress
//     private void CollectData()
//     {
//         if (!IsServer) return;

//         float fps = Mathf.Min(1f / Time.deltaTime, targetFrameRate); // Get the current measured frame rate or cap it at the target frame rate
//         dataBuilder.Clear(); // Reset data builder

//         // global or host info
//         dataBuilder.AppendFormat("{0},{1},{2},{3},{4},{5}", trial, numSubjects, angle, stopwatch.Elapsed.TotalSeconds, targetFrameRate, fps);

//         // per subject info
//         for (int i = 0; i < numSubjects; i++)
//         {
//             clients[i].PlayerObject.transform.GetPositionAndRotation(out Vector3 position, out Quaternion rotation);
//             dataBuilder.AppendFormat(",{0},{1},{2},{3},{4},{5}", position.x, position.y, position.z, rotation.eulerAngles.x, rotation.eulerAngles.y, rotation.eulerAngles.z);
//         }

//         dataBuilder.AppendLine();
//         dataBuffer += dataBuilder.ToString(); // Append the formatted data to the buffer
//     }

//     // Takes in two positions in [x,y,z] form and then returns true if the distance between them is less or equal to than the radius given.
//     bool IsInRadius(Vector3 pos, Vector3 center, float radius)
//     {
//         return Vector3.Distance(new Vector3(pos.x, 0, pos.z), new Vector3(center.x, 0, center.z)) <= radius;
//     }

//     // Plays the end audio clip
//     public void End()
//     {
//         PlayAudioClientRpc("end");
//     }

//     [ClientRpc]
//     private void PlayAudioClientRpc(string clipName)
//     {
//         AudioClip clip = null;

//         if (clipName == "begin") clip = begin;
//         else if (clipName == "end") clip = end;
//         else Debug.LogError($"Audio clip '{clipName}' not found.");

//         audioSource.PlayOneShot(clip);
//     }
// }