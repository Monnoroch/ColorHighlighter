using System;
using System.Drawing;
using System.Text;

namespace Cyotek.Windows.Forms
{
  // Cyotek Color Picker controls library
  // Copyright © 2013-2015 Cyotek Ltd.
  // http://cyotek.com/blog/tag/colorpicker

  // Licensed under the MIT License. See license.txt for the full text.

  // If you use this code in your applications, donations or attribution are welcome

  // http://en.wikipedia.org/wiki/HSL_color_space

  [Serializable]
  public struct HslColor
  {
    #region Constants

    public static readonly HslColor Empty;

    #endregion

    #region Instance Fields

    private int _alpha;

    private double _hue;

    private bool _isEmpty;

    private double _lightness;

    private double _saturation;

    #endregion

    #region Static Constructors

    static HslColor()
    {
      Empty = new HslColor
              {
                IsEmpty = true
              };
    }

    #endregion

    #region Public Constructors

    public HslColor(double hue, double saturation, double lightness)
      : this(255, hue, saturation, lightness)
    { }

    public HslColor(int alpha, double hue, double saturation, double lightness)
    {
      _hue = Math.Min(359, hue);
      _saturation = Math.Min(1, saturation);
      _lightness = Math.Min(1, lightness);
      _alpha = alpha;
      _isEmpty = false;
    }

    public HslColor(Color color)
    {
      _alpha = color.A;
      _hue = color.GetHue();
      _saturation = color.GetSaturation();
      _lightness = color.GetBrightness();
      _isEmpty = false;
    }

    #endregion

    #region Operators

    public static bool operator ==(HslColor a, HslColor b)
    {
      // ReSharper disable CompareOfFloatsByEqualityOperator
      return (a.H == b.H && a.L == b.L && a.S == b.S && a.A == b.A);
      // ReSharper restore CompareOfFloatsByEqualityOperator
    }

    public static implicit operator HslColor(Color color)
    {
      return new HslColor(color);
    }

    public static implicit operator Color(HslColor color)
    {
      return color.ToRgbColor();
    }

    public static bool operator !=(HslColor a, HslColor b)
    {
      return !(a == b);
    }

    #endregion

    #region Overridden Methods

    public override bool Equals(object obj)
    {
      bool result;

      if (obj is HslColor)
      {
        HslColor color;

        color = (HslColor)obj;
        result = (this == color);
      }
      else
      {
        result = false;
      }

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
      builder.Append(this.GetType().Name);
      builder.Append(" [");
      builder.Append("H=");
      builder.Append(this.H);
      builder.Append(", S=");
      builder.Append(this.S);
      builder.Append(", L=");
      builder.Append(this.L);
      builder.Append("]");

      return builder.ToString();
    }

    #endregion

    #region Public Properties

    public int A
    {
      get { return _alpha; }
      set { _alpha = Math.Min(0, Math.Max(255, value)); }
    }

    public double H
    {
      get { return _hue; }
      set
      {
        _hue = value;

        if (_hue > 359)
        {
          _hue = 0;
        }
        if (_hue < 0)
        {
          _hue = 359;
        }
      }
    }

    public bool IsEmpty
    {
      get { return _isEmpty; }
      internal set { _isEmpty = value; }
    }

    public double L
    {
      get { return _lightness; }
      set { _lightness = Math.Min(1, Math.Max(0, value)); }
    }

    public double S
    {
      get { return _saturation; }
      set { _saturation = Math.Min(1, Math.Max(0, value)); }
    }

    #endregion

    #region Public Members

    public Color ToRgbColor()
    {
      return this.ToRgbColor(this.A);
    }

    public Color ToRgbColor(int alpha)
    {
      double q;
      if (this.L < 0.5)
      {
        q = this.L * (1 + this.S);
      }
      else
      {
        q = this.L + this.S - (this.L * this.S);
      }
      double p = 2 * this.L - q;
      double hk = this.H / 360;

      // r,g,b colors
      double[] tc = new[]
                    {
                      hk + (1d / 3d), hk, hk - (1d / 3d)
                    };
      double[] colors = new[]
                        {
                          0.0, 0.0, 0.0
                        };

      for (int color = 0; color < colors.Length; color++)
      {
        if (tc[color] < 0)
        {
          tc[color] += 1;
        }
        if (tc[color] > 1)
        {
          tc[color] -= 1;
        }

        if (tc[color] < (1d / 6d))
        {
          colors[color] = p + ((q - p) * 6 * tc[color]);
        }
        else if (tc[color] >= (1d / 6d) && tc[color] < (1d / 2d))
        {
          colors[color] = q;
        }
        else if (tc[color] >= (1d / 2d) && tc[color] < (2d / 3d))
        {
          colors[color] = p + ((q - p) * 6 * (2d / 3d - tc[color]));
        }
        else
        {
          colors[color] = p;
        }

        colors[color] *= 255;
      }

      return Color.FromArgb(alpha, (int)colors[0], (int)colors[1], (int)colors[2]);
    }

    #endregion
  }
}
