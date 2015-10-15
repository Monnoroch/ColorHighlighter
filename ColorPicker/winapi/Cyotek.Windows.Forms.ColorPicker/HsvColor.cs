using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Linq;
using System.Text;

namespace Cyotek.Windows.Forms
{
  // http://www.easyrgb.com/index.php?X=MATH&H=20#text20
  // http://www.easyrgb.com/index.php?X=MATH&H=21#text21

  // TODO: Not working correctly, do not use

  [TypeConverter(typeof(ExpandableObjectConverter))]
  public struct HsvColor
  {
    #region Instance Fields

    private int _alpha;

    private double _hue;

    private double _value;

    private double _saturation;

    #endregion

    #region Constructors

    public HsvColor(double hue, double saturation, double value)
      : this(255, hue, saturation, value)
    { }

    public HsvColor(int alpha, double hue, double saturation, double value)
    {
      _hue = Math.Min(360, hue);
      _saturation = Math.Min(1, saturation);
      _value = Math.Min(1, value);
      _alpha = alpha;
    }

    public HsvColor(Color color)
    {
      double r;
      double g;
      double b;
      double max;
      double min;
      double delta;
      double deltaR;
      double deltaG;
      double deltaB;

      _alpha = color.A;
      r = (color.R / 255);                   //RGB from 0 to 255
      g = (color.G / 255);
      b = (color.B / 255);

      min = Math.Min(r, Math.Min(g, b));  //Min. value of RGB
      max = Math.Max(r, Math.Max(g, b));  //Max. value of RGB
      delta = max - min;        //Delta RGB value 

      _value = max;

      if (delta == 0)                     //This is a gray, no chroma...
      {
        _hue = 0;                         //HSV results from 0 to 1
        _saturation = 0;
      }
      else                                    //Chromatic data...
      {
        _saturation = delta / max;

        deltaR = (((max - r) / 6) + (delta / 2)) / delta;
        deltaG = (((max - g) / 6) + (delta / 2)) / delta;
        deltaB = (((max - b) / 6) + (delta / 2)) / delta;

        if (r == max)
          _hue = deltaB - deltaG;
        else if (g == max)
          _hue = (1 / 3) + deltaR - deltaB;
        else if (b == max)
          _hue = (2 / 3) + deltaG - deltaR;
        else
          _hue = 0;

        if (_hue < 0)
          _hue += 1;
        if (_hue > 1)
          _hue -= 1;
      }
    }

    #endregion

    #region Operators

    public static bool operator ==(HsvColor left, HsvColor right)
    {
      return (left.H == right.H && left.V == right.V && left.S == right.S && left.A == right.A);
    }

    public static bool operator !=(HsvColor left, HsvColor right)
    {
      return !(left == right);
    }

    #endregion

    #region Overridden Members

    public override bool Equals(object obj)
    {
      bool result;

      if (obj is HsvColor)
      {
        HsvColor color;

        color = (HsvColor)obj;
        result = (this == color);
      }
      else
        result = false;

      return result;
    }

    public override int GetHashCode()
    {
      return base.GetHashCode();
    }

    public override string ToString()
    {
      StringBuilder builder;

      builder = new StringBuilder();
      builder.Append(base.GetType().Name);
      builder.Append(" [");
      builder.Append("H=");
      builder.Append(this.H);
      builder.Append(", S=");
      builder.Append(this.S);
      builder.Append(", V=");
      builder.Append(this.V);
      builder.Append("]");

      return builder.ToString();
    }

    #endregion

    #region Properties

    public int A
    {
      get { return _alpha; }
      set { _alpha = value; }
    }

    public double H
    {
      get { return _hue; }
      set
      {
        _hue = value;

        if (_hue < 0)
          _hue += 1;
        if (_hue > 1)
          _hue -= 1;
      }
    }

    public double V
    {
      get { return _value; }
      set { _value = Math.Min(1, Math.Max(0, value)); }
    }

    public double S
    {
      get { return _saturation; }
      set { _saturation = Math.Min(1, Math.Max(0, value)); }
    }

    #endregion

    #region Members

    public Color ToRgbColor()
    {
      return this.ToRgbColor(this.A);
    }

    public Color ToRgbColor(int alpha)
    {
      int r;
      int g;
      int b;

      if (this.S == 0)                       //HSV from 0 to 1
      {
        r = (int)(this.V * 255);
        g = (int)(this.V * 255);
        b = (int)(this.V * 255);
      }
      else
      {
        double deltaH;
        double deltaR;
        double deltaG;
        double deltaB;
        double var_i;
        double var_1;
        double var_2;
        double var_3;

        deltaH = this.H * 6;
        if (deltaH == 6)
          deltaH = 0;   //H must be < 1
        var_i = Math.Floor(deltaH);
        var_1 = this.V * (1 - this.S);
        var_2 = this.V * (1 - this.S * (deltaH - var_i));
        var_3 = this.V * (1 - this.S * (1 - (deltaH - var_i)));

        if (var_i == 0) { deltaR = this.V; deltaG = var_3; deltaB = var_1; }
        else if (var_i == 1) { deltaR = var_2; deltaG = this.V; deltaB = var_1; }
        else if (var_i == 2) { deltaR = var_1; deltaG = this.V; deltaB = var_3; }
        else if (var_i == 3) { deltaR = var_1; deltaG = var_2; deltaB = this.V; }
        else if (var_i == 4) { deltaR = var_3; deltaG = var_1; deltaB = this.V; }
        else { deltaR = this.V; deltaG = var_1; deltaB = var_2; }

        r = (int)(deltaR * 255);      //RGB results from 0 to 255
        g = (int)(deltaG * 255);
        b = (int)(deltaB * 255);
      }

      return Color.FromArgb(alpha, r, g, b);
    }

    #endregion
  }
}
