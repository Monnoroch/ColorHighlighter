using System;
using System.ComponentModel;
using System.Drawing;
#if USEEXTERNALCYOTEKLIBS
using Cyotek.Drawing;

#endif

namespace Cyotek.Windows.Forms
{
  // Cyotek Color Picker controls library
  // Copyright © 2013-2015 Cyotek Ltd.
  // http://cyotek.com/blog/tag/colorpicker

  // Licensed under the MIT License. See license.txt for the full text.

  // If you use this code in your applications, donations or attribution are welcome

  public class LightnessColorSlider : ColorSlider, IColorEditor
  {
    #region Instance Fields

    private Color _color;

    #endregion

    #region Public Constructors

    public LightnessColorSlider()
    {
      this.BarStyle = ColorBarStyle.TwoColor;
      this.Color = Color.Black;
    }

    #endregion

    #region Events

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

    /// <summary>
    /// Raises the <see cref="ColorSlider.ValueChanged" /> event.
    /// </summary>
    /// <param name="e">The <see cref="EventArgs" /> instance containing the event data.</param>
    protected override void OnValueChanged(EventArgs e)
    {
      if (!this.LockUpdates)
      {
        HslColor color;

        this.LockUpdates = true;
        color = new HslColor(this.Color);
        color.L = this.Value / 100D;
        _color = color.ToRgbColor();
        this.OnColorChanged(e);
        this.LockUpdates = false;
      }

      base.OnValueChanged(e);
    }

    #endregion

    #region Public Properties

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

          if (!this.LockUpdates)
          {
            this.LockUpdates = true;
            this.Value = (float)new HslColor(value).L * 100;
            this.OnColorChanged(EventArgs.Empty);
            this.LockUpdates = false;
          }
        }
      }
    }

    #endregion

    #region Protected Properties

    /// <summary>
    /// Gets or sets a value indicating whether input changes should be processed.
    /// </summary>
    /// <value><c>true</c> if input changes should be processed; otherwise, <c>false</c>.</value>
    protected bool LockUpdates { get; set; }

    #endregion

    #region Protected Members

    protected virtual void CreateScale()
    {
      HslColor color;

      color = new HslColor(this.Color);

      color.L = 0;
      this.Color1 = color.ToRgbColor();

      color.L = 1;
      this.Color2 = color.ToRgbColor();
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
