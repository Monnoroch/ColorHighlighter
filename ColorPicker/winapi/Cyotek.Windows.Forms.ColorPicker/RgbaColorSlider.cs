using System;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Linq;
using System.Windows.Forms;

namespace Cyotek.Windows.Forms
{
  // Cyotek Color Picker controls library
  // Copyright © 2013-2015 Cyotek Ltd.
  // http://cyotek.com/blog/tag/colorpicker

  // Licensed under the MIT License. See license.txt for the full text.

  // If you use this code in your applications, donations or attribution are welcome

  public class RgbaColorSlider : ColorSlider
  {
    #region Instance Fields

    private Brush _cellBackgroundBrush;

    private RgbaChannel _channel;

    private Color _color;

    #endregion

    #region Public Constructors

    public RgbaColorSlider()
    {
      this.BarStyle = ColorBarStyle.Custom;
      this.Maximum = 255;
      this.Color = Color.Black;
      this.CreateScale();
    }

    #endregion

    #region Events

    /// <summary>
    /// Occurs when the Channel property value changes
    /// </summary>
    [Category("Property Changed")]
    public event EventHandler ChannelChanged;

    /// <summary>
    /// Occurs when the Color property value changes
    /// </summary>
    [Category("Property Changed")]
    public event EventHandler ColorChanged;

    #endregion

    #region Overridden Properties

    [Browsable(false)]
    [DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)]
    public override ColorBarStyle BarStyle
    {
      get { return base.BarStyle; }
      set { base.BarStyle = value; }
    }

    [Browsable(false)]
    [DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)]
    public override Color Color1
    {
      get { return base.Color1; }
      set { base.Color1 = value; }
    }

    [Browsable(false)]
    [DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)]
    public override Color Color2
    {
      get { return base.Color2; }
      set { base.Color2 = value; }
    }

    [Browsable(false)]
    [DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)]
    public override Color Color3
    {
      get { return base.Color3; }
      set { base.Color3 = value; }
    }

    [Browsable(false)]
    [DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)]
    public override float Maximum
    {
      get { return base.Maximum; }
      set { base.Maximum = value; }
    }

    [Browsable(false)]
    [DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)]
    public override float Minimum
    {
      get { return base.Minimum; }
      set { base.Minimum = value; }
    }

    public override float Value
    {
      get { return base.Value; }
      set { base.Value = (int)value; }
    }

    #endregion

    #region Overridden Methods

    protected override void Dispose(bool disposing)
    {
      if (disposing)
      {
        if (_cellBackgroundBrush != null)
        {
          _cellBackgroundBrush.Dispose();
        }
      }

      base.Dispose(disposing);
    }

    protected override void PaintBar(PaintEventArgs e)
    {
      if (this.Color.A != 255)
      {
        if (_cellBackgroundBrush == null)
        {
          _cellBackgroundBrush = this.CreateTransparencyBrush();
        }

        e.Graphics.FillRectangle(_cellBackgroundBrush, this.BarBounds);
      }

      base.PaintBar(e);
    }

    #endregion

    #region Public Properties

    [Category("Appearance")]
    [DefaultValue(typeof(RgbaChannel), "Red")]
    public virtual RgbaChannel Channel
    {
      get { return _channel; }
      set
      {
        if (this.Channel != value)
        {
          _channel = value;

          this.OnChannelChanged(EventArgs.Empty);
        }
      }
    }

    [Category("Appearance")]
    [DefaultValue(typeof(Color), "Black")]
    public virtual Color Color
    {
      get { return _color; }
      set
      {
        if (this.Color != value)
        {
          _color = value;

          this.OnColorChanged(EventArgs.Empty);
        }
      }
    }

    #endregion

    #region Protected Members

    protected virtual void CreateScale()
    {
      this.CustomColors = new ColorCollection(Enumerable.Range(0, 254).Select(i => Color.FromArgb(this.Channel == RgbaChannel.Alpha ? i : this.Color.A, this.Channel == RgbaChannel.Red ? i : this.Color.R, this.Channel == RgbaChannel.Green ? i : this.Color.G, this.Channel == RgbaChannel.Blue ? i : this.Color.B)));
    }

    protected virtual Brush CreateTransparencyBrush()
    {
      Type type;

      type = typeof(RgbaColorSlider);

      using (Bitmap background = new Bitmap(type.Assembly.GetManifestResourceStream(string.Concat(type.Namespace, ".Resources.cellbackground.png"))))
      {
        return new TextureBrush(background, WrapMode.Tile);
      }
    }

    /// <summary>
    /// Raises the <see cref="ChannelChanged" /> event.
    /// </summary>
    /// <param name="e">The <see cref="EventArgs" /> instance containing the event data.</param>
    protected virtual void OnChannelChanged(EventArgs e)
    {
      EventHandler handler;

      this.CreateScale();

      handler = this.ChannelChanged;

      if (handler != null)
      {
        handler(this, e);
      }
    }

    /// <summary>
    /// Raises the <see cref="ColorChanged" /> event.
    /// </summary>
    /// <param name="e">The <see cref="EventArgs" /> instance containing the event data.</param>
    protected virtual void OnColorChanged(EventArgs e)
    {
      EventHandler handler;

      this.CreateScale();
      this.Invalidate();

      handler = this.ColorChanged;

      if (handler != null)
      {
        handler(this, e);
      }
    }

    #endregion
  }
}
