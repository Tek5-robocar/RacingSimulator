using UnityEditor;
using UnityEngine;

public static class ProjectFileGenerator
{
    [MenuItem("Tools/Generate Project Files")]
    public static void Generate()
    {
        // Method 1: Using the new public API (preferred)
        UnityEditor.Compilation.CompilationPipeline.RequestScriptCompilation();
        
        // Method 2: Alternative approach
        EditorApplication.ExecuteMenuItem("Assets/Open C# Project");
        
        // Method 3: Trigger asset refresh which sometimes helps
        AssetDatabase.Refresh();
        
        Debug.Log("Project files generation requested");
    }
}
