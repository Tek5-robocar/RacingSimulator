using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.Serialization.Formatters.Binary;
using UnityEngine;

[Serializable]
public class TrackData
{
    public string name;
    public float score;

    public TrackData(string name, float score)
    {
        this.name = name;
        this.score = score;
    }
}

[Serializable]
public class TrackDataListSerializable
{
    public List<TrackData> tracks = new();
}

public static class BinarySaveManager
{
    private static readonly string FilePath = Application.persistentDataPath + "/tracks.dat";

    public static void SaveTracks(List<(string, float)> tracks)
    {
        var formatter = new BinaryFormatter();
        var file = File.Create(FilePath);

        var data = new TrackDataListSerializable();
        data.tracks = tracks.ConvertAll(t => new TrackData(t.Item1, t.Item2));

        formatter.Serialize(file, data);
        file.Close();
    }

    public static List<(string, float)> LoadTracks()
    {
        if (File.Exists(FilePath))
        {
            var formatter = new BinaryFormatter();
            var file = File.Open(FilePath, FileMode.Open);

            var data = (TrackDataListSerializable)formatter.Deserialize(file);
            file.Close();

            return data.tracks.ConvertAll(t => (t.name, t.score));
        }

        return new List<(string, float)>();
    }
}