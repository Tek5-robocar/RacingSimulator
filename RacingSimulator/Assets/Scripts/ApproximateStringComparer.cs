using System;
using System.Collections.Generic;
using System.Linq;

public class ApproximateStringComparer : IEqualityComparer<string>
{
    private readonly int _tolerance;

    public ApproximateStringComparer(int tolerance)
    {
        _tolerance = tolerance; // Set the allowed tolerance (difference)
    }

    public bool Equals(string x, string y)
    {
        if (x == null || y == null)
            return false;

        var xNumbers = x.Split(';').Select(int.Parse).ToArray();
        var yNumbers = y.Split(';').Select(int.Parse).ToArray();

        if (xNumbers.Length != 6 || yNumbers.Length != 6)
            return false;

        for (int i = 0; i < 6; i++)
        {
            if (Math.Abs(xNumbers[i] - yNumbers[i]) > _tolerance)
                return false;
        }

        return true;
    }

    public int GetHashCode(string obj)
    {
        return 0;
    }
}