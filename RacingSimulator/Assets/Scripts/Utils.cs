using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEngine;

public class Utils
{
    public static string[] GetCsvInfosFromRegex(string filePath, string pattern)
    {
        try
        {
            string content = File.ReadAllText(filePath);

            if (content == "")
                return null;
            
            Match match = Regex.Match(content, pattern);

            if (match.Success)
            {
                string allFile = match.Groups[0].Value;

                if (content.Replace(allFile, "") != "")
                {
                    Debug.LogError("File format not right");
                    return null;
                }

                return match.Groups.Select(grp => grp.Value).Skip(1).ToArray();
            }
            Debug.LogError("File format not right");
            return null;
        }
        catch (Exception ex)
        {
            Debug.LogError($"Error reading Csv file: {ex.Message}");
            return null;
        }
    }
    
    private static void TraverseChildren<T>(Transform parent, List<T> wantedComponentList)
    {
        foreach (Transform child in parent)
        {
            T[] components = child.gameObject.GetComponents<T>();
            foreach (T component in components)
                wantedComponentList.Add(component);
            TraverseChildren(child, wantedComponentList);
        }
    }

    public static List<T> GetChildrenOfType<T>(GameObject parent)
    {
        List<T> children = new List<T>();

        TraverseChildren<T>(parent.transform, children);
        return children;
    }
    
    public static void ApplyTextureOnMeshRenderers(List<MeshRenderer> meshRenderers, Texture2D texture)
    {
        foreach (var meshRenderer in meshRenderers) meshRenderer.material.mainTexture = texture;
    }
}