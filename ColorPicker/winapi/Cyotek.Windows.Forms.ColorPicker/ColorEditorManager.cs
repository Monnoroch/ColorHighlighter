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

  /// <summary>
  /// Represents a control that binds multiple editors together as a single composite unit.
  /// </summary>
  [DefaultEvent("ColorChanged")]
  public class ColorEditorManager : Component, IColorEditor
  {
    #region Instance Fields

    private Color _color;

    private ColorEditor _colorEditor;

    private ColorGrid _grid;

    private HslColor _hslColor;

    private LightnessColorSlider _lightnessColorSlider;

    private ScreenColorPicker _screenColorPicker;

    private ColorWheel _wheel;

    #endregion

    #region Events

    /// <summary>
    /// Occurs when the Color property value changes
    /// </summary>
    [Category("Property Changed")]
    public event EventHandler ColorChanged;

    /// <summary>
    /// Occurs when the ColorEditor property value changes
    /// </summary>
    [Category("Property Changed")]
    public event EventHandler ColorEditorChanged;

    /// <summary>
    /// Occurs when the Grid property value changes
    /// </summary>
    [Category("Property Changed")]
    public event EventHandler ColorGridChanged;

    /// <summary>
    /// Occurs when the Wheel property value changes
    /// </summary>
    [Category("Property Changed")]
    public event EventHandler ColorWheelChanged;

    /// <summary>
    /// Occurs when the LightnessColorSlider property value changes
    /// </summary>
    [Category("Property Changed")]
    public event EventHandler LightnessColorSliderChanged;

    /// <summary>
    /// Occurs when the ScreenColorPicker property value changes
    /// </summary>
    [Category("Property Changed")]
    public event EventHandler ScreenColorPickerChanged;

    #endregion

    #region Public Properties

    /// <summary>
    /// Gets or sets the component color.
    /// </summary>
    /// <value>The component color.</value>
    [Browsable(false)]
    [DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)]
    public virtual Color Color
    {
      get { return _color; }
      set
      {
        if (_color != value)
        {
          _color = value;
          _hslColor = new HslColor(value);

          this.OnColorChanged(EventArgs.Empty);
        }
      }
    }

    /// <summary>
    /// Gets or sets the linked <see cref="ColorEditor"/>.
    /// </summary>
    [Category("Behavior")]
    [DefaultValue(typeof(ColorEditor), null)]
    public virtual ColorEditor ColorEditor
    {
      get { return _colorEditor; }
      set
      {
        if (this.ColorEditor != value)
        {
          _colorEditor = value;

          this.OnColorEditorChanged(EventArgs.Empty);
        }
      }
    }

    /// <summary>
    /// Gets or sets the linked <see cref="ColorGrid"/>.
    /// </summary>
    [Category("Behavior")]
    [DefaultValue(typeof(ColorGrid), null)]
    public virtual ColorGrid ColorGrid
    {
      get { return _grid; }
      set
      {
        if (this.ColorGrid != value)
        {
          _grid = value;

          this.OnColorGridChanged(EventArgs.Empty);
        }
      }
    }

    /// <summary>
    /// Gets or sets the linked <see cref="ColorWheel"/>.
    /// </summary>
    [Category("Behavior")]
    [DefaultValue(typeof(ColorWheel), null)]
    public virtual ColorWheel ColorWheel
    {
      get { return _wheel; }
      set
      {
        if (this.ColorWheel != value)
        {
          _wheel = value;

          this.OnColorWheelChanged(EventArgs.Empty);
        }
      }
    }

    /// <summary>
    /// Gets or sets the component color as a HSL structure.
    /// </summary>
    /// <value>The component color.</value>
    [Browsable(false)]
    [DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)]
    public virtual HslColor HslColor
    {
      get { return _hslColor; }
      set
      {
        if (this.HslColor != value)
        {
          _hslColor = value;
          _color = value.ToRgbColor();

          this.OnColorChanged(EventArgs.Empty);
        }
      }
    }

    /// <summary>
    /// Gets or sets the linked <see cref="LightnessColorSlider"/>.
    /// </summary>
    [Category("Behavior")]
    [DefaultValue(typeof(LightnessColorSlider), null)]
    public virtual LightnessColorSlider LightnessColorSlider
    {
      get { return _lightnessColorSlider; }
      set
      {
        if (this.LightnessColorSlider != value)
        {
          _lightnessColorSlider = value;

          this.OnLightnessColorSliderChanged(EventArgs.Empty);
        }
      }
    }

    /// <summary>
    /// Gets or sets the linked <see cref="ScreenColorPicker"/>.
    /// </summary>
    [Category("Behavior")]
    [DefaultValue(typeof(ScreenColorPicker), null)]
    public virtual ScreenColorPicker ScreenColorPicker
    {
      get { return _screenColorPicker; }
      set
      {
        if (this.ScreenColorPicker != value)
        {
          _screenColorPicker = value;

          this.OnScreenColorPickerChanged(EventArgs.Empty);
        }
      }
    }

    #endregion

    #region Protected Properties

    /// <summary>
    /// Gets or sets a value indicating whether updating of linked components is disabled.
    /// </summary>
    /// <value><c>true</c> if updated of linked components is disabled; otherwise, <c>false</c>.</value>
    protected bool LockUpdates { get; set; }

    #endregion

    #region Protected Members

    /// <summary>
    /// Binds events for the specified editor.
    /// </summary>
    /// <param name="control">The <see cref="IColorEditor"/> to bind to.</param>
    protected virtual void BindEvents(IColorEditor control)
    {
      control.ColorChanged += this.ColorChangedHandler;
    }

    /// <summary>
    /// Raises the <see cref="ColorChanged" /> event.
    /// </summary>
    /// <param name="e">The <see cref="EventArgs" /> instance containing the event data.</param>
    protected virtual void OnColorChanged(EventArgs e)
    {
      EventHandler handler;

      this.Synchronize(this);

      handler = this.ColorChanged;

      if (handler != null)
      {
        handler(this, e);
      }
    }

    /// <summary>
    /// Raises the <see cref="ColorEditorChanged" /> event.
    /// </summary>
    /// <param name="e">The <see cref="EventArgs" /> instance containing the event data.</param>
    protected virtual void OnColorEditorChanged(EventArgs e)
    {
      EventHandler handler;

      if (this.ColorEditor != null)
      {
        this.BindEvents(this.ColorEditor);
      }

      handler = this.ColorEditorChanged;

      if (handler != null)
      {
        handler(this, e);
      }
    }

    /// <summary>
    /// Raises the <see cref="ColorGridChanged" /> event.
    /// </summary>
    /// <param name="e">The <see cref="EventArgs" /> instance containing the event data.</param>
    protected virtual void OnColorGridChanged(EventArgs e)
    {
      EventHandler handler;

      if (this.ColorGrid != null)
      {
        this.BindEvents(this.ColorGrid);
      }

      handler = this.ColorGridChanged;

      if (handler != null)
      {
        handler(this, e);
      }
    }

    /// <summary>
    /// Raises the <see cref="ColorWheelChanged" /> event.
    /// </summary>
    /// <param name="e">The <see cref="EventArgs" /> instance containing the event data.</param>
    protected virtual void OnColorWheelChanged(EventArgs e)
    {
      EventHandler handler;

      if (this.ColorWheel != null)
      {
        this.BindEvents(this.ColorWheel);
      }

      handler = this.ColorWheelChanged;

      if (handler != null)
      {
        handler(this, e);
      }
    }

    /// <summary>
    /// Raises the <see cref="LightnessColorSliderChanged" /> event.
    /// </summary>
    /// <param name="e">The <see cref="EventArgs" /> instance containing the event data.</param>
    protected virtual void OnLightnessColorSliderChanged(EventArgs e)
    {
      EventHandler handler;

      if (this.LightnessColorSlider != null)
      {
        this.BindEvents(this.LightnessColorSlider);
      }

      handler = this.LightnessColorSliderChanged;

      if (handler != null)
      {
        handler(this, e);
      }
    }

    /// <summary>
    /// Raises the <see cref="ScreenColorPickerChanged" /> event.
    /// </summary>
    /// <param name="e">The <see cref="EventArgs" /> instance containing the event data.</param>
    protected virtual void OnScreenColorPickerChanged(EventArgs e)
    {
      EventHandler handler;

      if (this.ScreenColorPicker != null)
      {
        this.BindEvents(this.ScreenColorPicker);
      }

      handler = this.ScreenColorPickerChanged;

      if (handler != null)
      {
        handler(this, e);
      }
    }

    /// <summary>
    /// Sets the color of the given editor.
    /// </summary>
    /// <param name="control">The <see cref="IColorEditor"/> to update.</param>
    /// <param name="sender">The <see cref="IColorEditor"/> triggering the update.</param>
    protected virtual void SetColor(IColorEditor control, IColorEditor sender)
    {
      if (control != null && control != sender)
      {
        control.Color = sender.Color;
      }
    }

    /// <summary>
    /// Synchronizes linked components with the specified <see cref="IColorEditor"/>.
    /// </summary>
    /// <param name="sender">The <see cref="IColorEditor"/> triggering the update.</param>
    protected virtual void Synchronize(IColorEditor sender)
    {
      if (!this.LockUpdates)
      {
        try
        {
          this.LockUpdates = true;
          this.SetColor(this.ColorGrid, sender);
          this.SetColor(this.ColorWheel, sender);
          this.SetColor(this.ScreenColorPicker, sender);
          this.SetColor(this.ColorEditor, sender);
          this.SetColor(this.LightnessColorSlider, sender);
        }
        finally
        {
          this.LockUpdates = false;
        }
      }
    }

    #endregion

    #region Event Handlers

    /// <summary>
    /// Handler for linked controls.
    /// </summary>
    /// <param name="sender">The sender.</param>
    /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
    private void ColorChangedHandler(object sender, EventArgs e)
    {
      if (!this.LockUpdates)
      {
        IColorEditor source;

        source = (IColorEditor)sender;

        this.LockUpdates = true;
        this.Color = source.Color;
        this.LockUpdates = false;
        this.Synchronize(source);
      }
    }

    #endregion
  }
}
