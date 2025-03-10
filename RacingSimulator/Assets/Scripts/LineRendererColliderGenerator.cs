using UnityEngine;

[RequireComponent(typeof(LineRenderer))]
public class LineRendererColliderGenerator : MonoBehaviour
{
    private float _colliderWidth; // Width of the collider
    private LineRenderer lineRenderer;

    private void Start()
    {
        lineRenderer = GetComponent<LineRenderer>();
        _colliderWidth = lineRenderer.startWidth;
        CreateColliders();
        var outline = gameObject.AddComponent<Outline>();

        outline.OutlineMode = Outline.Mode.OutlineAll;
        outline.OutlineColor = Color.white;
        outline.OutlineWidth = 5f;
    }

    private void CreateColliders()
    {
        var numPositions = lineRenderer.positionCount;

        for (var i = 0; i < numPositions - 1; i++)
        {
            var startPos = lineRenderer.GetPosition(i);
            var endPos = lineRenderer.GetPosition(i + 1);

            var newCollider = new GameObject(lineRenderer.name + "Collider").AddComponent<BoxCollider>();

            newCollider.tag = lineRenderer.tag;
            newCollider.gameObject.layer = lineRenderer.gameObject.layer;

            newCollider.transform.SetParent(transform);

            var colliderPos = (transform.TransformPoint(startPos) + transform.TransformPoint(endPos)) / 2;
            newCollider.transform.position = colliderPos;
            
            var distance = Vector3.Distance(startPos, endPos);
            newCollider.size = new Vector3(distance, 10, 0.1f);

            var direction = (endPos - startPos).normalized;
            Vector3 normal = Vector3.Cross(direction, Vector3.up).normalized;
            newCollider.transform.rotation = Quaternion.LookRotation(normal);
            newCollider.transform.Rotate(new Vector3(0, 90, 0));

            newCollider.isTrigger = true;
        }
    }
}