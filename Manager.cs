using UnityEngine;
using System.Collections.Generic;
using System;
using System.Linq;
using System.Collections;
using System.IO;
using System.IO.Ports;
using TMPro;
using UnityEngine.Android;
using UnityEngine.UIElements;

public class Manager : MonoBehaviour
{
    // VR Rig Settings
    public Transform rig;
    public GameObject compassNeedle, textScore;

    // Motor Settings
    public int numMotors = 8;
    private const byte MotorMaxIntensity = 250, StartByte = 255, EndByte = 254;

    // Serial Connection Settings
    private const string UsbPermission = "android.permission.USB_PERMISSION";
    private const int BaudRate = 115200, DataBits = 8, StopBits = 1, Parity = 0, ProductId = 0067;

    public string subjectNum; // Subject number for data logging
    public GameObject[] poles;
    public Vector3[] polePositions = new Vector3[] { new(2, 0, 1), new(2, 0, -1), new(-2, 0, -1) };
    private string platform = null;
    private string csvFilePath; // Path to the CSV output file
    private StreamWriter csvWriter; // CSV writer for logging data
    private AndroidJavaObject serialDevice; // Android
    private SerialPort serialPort; // PC
    private int currentPoleIndex = 0; // Tracks progress on which pole is reached
    private float startTime = 0f, lastWriteTime = 0f, resetTime = 0f;
    private readonly List<string> bufferedData = new(); // Buffer for CSV data to avoid frequent disk writes
    private const float PoleDistanceThreshold = 0.5f;  // Distance threshold for pole progress
    private const float BufferFlushInterval = 1.0f; // Time interval to flush CSV buffer (in seconds)

    // Start is called before the first frame update
    void Start()
    {
        if (Application.platform == RuntimePlatform.WindowsEditor ||
            Application.platform == RuntimePlatform.WindowsPlayer)
            platform = "PC";
        else if (Application.platform == RuntimePlatform.Android)
            platform = "Android";
        else platform = null;

        if (!Permission.HasUserAuthorizedPermission(UsbPermission)) Permission.RequestUserPermission(UsbPermission);
        if (InitializeUsbDevice()) SetUp();
    }

    private bool InitializeUsbDevice()
    {
        return platform switch
        {
            "PC" => InitializeUsbDevicePC(),
            "Android" => InitializeUsbDeviceAndroid(),
            _ => false
        };
    }

    private bool InitializeUsbDevicePC()
    {
        try
        {
            serialPort = new("COM7", BaudRate, Parity, DataBits, (StopBits)StopBits);
            serialPort.Open();

            if (serialPort.IsOpen)
            {
                Debug.Log("USB Serial Device initialized successfully (PC)");
                return true;
            }
            else
            {
                Debug.LogError("Failed to open USB Serial Port.");
                return false;
            }
        }
        catch (Exception e)
        {
            Debug.LogError("Error in USB setup (PC): " + e.Message);
            return false;
        }
    }

    private bool InitializeUsbDeviceAndroid()
    {
        try
        {
            using AndroidJavaClass unityPlayer = new("com.unity3d.player.UnityPlayer");
            var currentActivity = unityPlayer.GetStatic<AndroidJavaObject>("currentActivity");
            var usbManager = currentActivity.Call<AndroidJavaObject>("getSystemService", "usb");
            var deviceList = usbManager.Call<AndroidJavaObject>("getDeviceList");
            AndroidJavaObject usbDevice = null;
            var deviceIterator = deviceList.Call<AndroidJavaObject>("values").Call<AndroidJavaObject>("iterator");

            while (deviceIterator.Call<bool>("hasNext"))
            {
                var device = deviceIterator.Call<AndroidJavaObject>("next");
                var foundId = device.Call<int>("getProductId");
                Debug.Log($"Found {foundId}");

                // If product ID matches, assign device and break
                if (foundId == ProductId)
                {
                    usbDevice = device;
                    Debug.Log($"Found USB device: {usbDevice.Call<string>("toString")}");
                    break;
                }
            }

            if (usbDevice == null)
            {
                Debug.LogError("No USB device with matching product ID found.");
                return false;
            }

            // Open a connection to the USB device
            AndroidJavaObject usbConnection = usbManager.Call<AndroidJavaObject>("openDevice", usbDevice);
            
            // Create the UsbSerialDevice using the device and connection
            //TODO: FIX
            serialDevice = new("com.hoho.android.usbserial.driver.UsbSerialDevice", usbDevice, usbConnection);
            
            if (serialDevice == null)
            {
                Debug.LogError("Failed to create USB serial device");
                return false;
            }

            // Initialize the serial device with appropriate settings
            serialDevice.Call("open");
            serialDevice.Call("setBaudRate", BaudRate);
            serialDevice.Call("setDataBits", DataBits);
            serialDevice.Call("setStopBits", StopBits);
            serialDevice.Call("setParity", Parity);

            Debug.Log("USB Serial Device initialized successfully");
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError("Error in USB setup: " + e.Message);
            return false;
        }
    }

    void SetUp()
    {
        csvFilePath = Path.Combine(Application.persistentDataPath, $"Subj{subjectNum}_data.csv"); // Set the CSV file path
        csvWriter = new(csvFilePath, true); // Initialize the CSV writer with appending enabled
        csvWriter.WriteLine("Time,Trial,PositionX,PositionY,PositionZ,RotationX,RotationY,RotationZ"); // Write CSV header
        StartCoroutine(Main());
    }

    private IEnumerator Main()
    {
        yield return StartCoroutine(TestMotors());
        InstantiatePoles();
    }

    // Method to test motor functionality by vibrating each motor
    private IEnumerator TestMotors()
    {
        yield return new WaitForSeconds(2f); // Allow visuals to load before testing

        // Test each motor twice (2 * numMotors), vibrating each motor for 1 second
        for (int i = 0; i < numMotors * 2; i++)
        {
            Debug.Log($"Testing motor #{i % numMotors}...");
            yield return StartCoroutine(ActivateMotor(i % numMotors, 1));
        }

        Debug.Log("Done verifying motors");
        yield return new WaitForSeconds(2f); // Wait 2 seconds after the motor tests are completed
    }

    private IEnumerator ActivateMotor(int motorToActivate, float duration)
    {
        // Send signal to activate motor
        byte[] motorIntensities = new byte[numMotors];
        motorIntensities[motorToActivate] = MotorMaxIntensity;
        Array.Reverse(motorIntensities); // Reverse motor intensities for Arduino communication
        byte[] dataToSend = new byte[] { StartByte }.Concat(motorIntensities).Concat(new byte[] { EndByte }).ToArray(); // Combine start/end bytes and motor intensities
        Debug.Log($"Sending Data (Activate): {BitConverter.ToString(dataToSend)}");
        if (!SendData(dataToSend)) yield break;

        // Let the motor run for 1 second
        yield return new WaitForSeconds(duration);

        // Send signal to deactivate motor
        motorIntensities[motorToActivate] = 0;
        dataToSend = new byte[] { StartByte }.Concat(motorIntensities).Concat(new byte[] { EndByte }).ToArray(); // Combine start/end bytes and motor intensities
        Debug.Log($"Sending Data (Deactivate): {BitConverter.ToString(dataToSend)}");
        if (!SendData(dataToSend)) yield break;

        // Wait briefly after deactivation
        yield return new WaitForSeconds(2f);
    }

    private void ActivateAllMotors(float duration)
    {
        for (int i = 0; i < numMotors; i++) StartCoroutine(ActivateMotor(i, duration));
    }

    private bool SendData(byte[] dataToSend)
    {
        if (platform == "PC")
        {
            if (serialPort != null && serialPort.IsOpen)
            {
                try
                {
                    serialPort.Write(dataToSend, 0, dataToSend.Length);
                    return true;
                }
                catch (Exception e)
                {
                    Debug.LogError($"Failed to write data via serialPort: {e.Message}");
                    return false; // Failed to send data
                }
            }
            else
            {
                Debug.LogError("serialPort is null or not open.");
                return false; // serialPort is not valid
            }
        }
        else if (platform == "Android")
        {
            if (serialDevice != null)
            {
                try
                {
                    serialDevice?.Call("write", new AndroidJavaObject("byte[]", dataToSend));
                    return true;
                }
                catch (Exception e)
                {
                    Debug.LogError($"Failed to write data via serialDevice: {e.Message}");
                    return false; // Failed to send data
                }
            }
            else
            {
                Debug.LogError("serialDevice is null.");
                return false; // serialDevice is not valid
            }
        }
        else
        {
            Debug.LogError("Platform not supported.");
            return false;
        }
    }

    private void InstantiatePoles()
    {
        int numPoles = polePositions.Length;
        for (int i = 0; i < numPoles; i++) Instantiate(poles[i], polePositions[i], Quaternion.identity);
    }

    // Update is called once per frame to handle the game logic
    void FixedUpdate()
    {
        // Collect and log current data, writing to the file immediately
        rig.GetPositionAndRotation(out Vector3 position, out Quaternion rotation);
        string data = $"{Time.fixedDeltaTime},{currentPoleIndex},{position.x},{position.y},{position.z},{rotation.eulerAngles.x},{rotation.eulerAngles.y},{rotation.eulerAngles.z}";
        bufferedData.Add(data);

        if (Time.time - lastWriteTime > BufferFlushInterval)
        {
            foreach(var line in bufferedData) csvWriter.WriteLine(line);
            csvWriter.Flush();
            bufferedData.Clear();
            lastWriteTime = Time.time;
        }

        // Update the compass needle's rotation to point towards the current pole target
        float desiredAngle = CalculateDesiredAngle(position);
        compassNeedle.transform.eulerAngles = new(compassNeedle.transform.eulerAngles.x, desiredAngle, compassNeedle.transform.eulerAngles.z);

        // Update the UI text with the current and desired angles
        string screenMessage = $"Current Angle: {rotation.eulerAngles.y}\nDesired: {desiredAngle}";
        textScore.GetComponent<TextMeshProUGUI>().text = screenMessage;

        // Check if the rig has reached the pole's location
        if (CheckPoleProgress(position))
        {
            // Trigger vibration to all motors when reaching the first pole
            if (currentPoleIndex == 1) ActivateAllMotors(2f);

            // Enqueue additional motor commands based on time intervals
            if (Time.time - startTime > 1f)
            {
                ActivateAllMotors(0.3f); // Default vibration for 0.3 seconds
                ActivateAllMotors(0.7f); // Additional vibration command after a delay
                startTime = Time.time; // Update the start time for the next interval
            }
        }

        // Reset serial port buffers every 10 seconds
        if (Time.time - resetTime > 10f)
        {
            if (platform == "PC")
            {
                serialPort?.DiscardInBuffer();
                serialPort?.DiscardOutBuffer();
            }
            else if (platform == "Android")
            {
                serialDevice?.Call("discardInBuffer");
                serialDevice?.Call("discardOutBuffer");
            }
            else Debug.LogError("Serial device not initialized or open.");
            
            resetTime = Time.time; // Update reset time
        }
    }

    private float CalculateDesiredAngle(Vector3 position)
    {
        Vector3 targetPole = polePositions[currentPoleIndex];
        float dx = targetPole.x - position.x;
        float dz = targetPole.z - position.z;
        return Mathf.Atan2(dx, dz) * Mathf.Rad2Deg; // Convert radians to degrees
    }

    private bool CheckPoleProgress(Vector3 currentPosition)
    {
        Vector3 targetPole = polePositions[currentPoleIndex];
        float distanceToDest = Vector3.Distance(currentPosition, targetPole);

        if (distanceToDest < PoleDistanceThreshold) // If close enough to the pole, move to the next
        {
            currentPoleIndex++;
            return currentPoleIndex < polePositions.Length; // Return true if there are more poles to visit
        }

        return false; // Otherwise, keep checking
    }

    // Cleanup on application quit (stop the motor thread and close the serial port)
    void OnApplicationQuit()
    {
        StopAllCoroutines(); // Stop all running coroutines
        csvWriter.Close(); // Close the CSV file writer

        if (serialDevice != null)
        {
            try
            {
                if (platform == "PC")
                {
                    serialPort?.Close();
                    Debug.Log("USB Serial device closed.");
                }
                else if (platform == "Android")
                {
                    serialDevice?.Call("close");
                    Debug.Log("USB Serial device closed.");
                }
                else Debug.LogError("Serial device not initialized or open.");
            }
            catch (Exception e)
            {
                Debug.LogError("Failed to close USB device: " + e.Message);
            }
        }
    }
}