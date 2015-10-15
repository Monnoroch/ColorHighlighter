using System;
using System.ComponentModel;
using System.Drawing;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Windows.Forms;
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
    /// Represents a control that allows the editing of a color in a variety of ways.
    /// </summary>
    [DefaultProperty("Color")]
    [DefaultEvent("ColorChanged")]
    public partial class ColorEditor : UserControl, IColorEditor
    {
        #region Instance Fields

        private Color _color;

        private HslColor _hslColor;

        private Orientation _orientation;

        private bool _showAlphaChannel;

        #endregion

        #region Public Constructors

        /// <summary>
        /// Initializes a new instance of the <see cref="ColorEditor"/> class.
        /// </summary>
        public ColorEditor()
        {
            this.InitializeComponent();

            this.Color = Color.Black;
            this.Orientation = Orientation.Vertical;
            this.Size = new Size(200, 260);
            this.ShowAlphaChannel = true;
            
            this.LockUpdates = false;
        }

        #endregion

        #region Events

        /// <summary>
        /// Occurs when the Color property value changes
        /// </summary>
        [Category("Property Changed")]
        public event EventHandler ColorChanged;

        /// <summary>
        /// Occurs when the Orientation property value changes
        /// </summary>
        [Category("Property Changed")]
        public event EventHandler OrientationChanged;

        /// <summary>
        /// Occurs when the ShowAlphaChannel property value changes
        /// </summary>
        [Category("Property Changed")]
        public event EventHandler ShowAlphaChannelChanged;

        #endregion

        #region Overridden Methods

        /// <summary>
        /// Raises the <see cref="E:System.Windows.Forms.Control.DockChanged" /> event.
        /// </summary>
        /// <param name="e">An <see cref="T:System.EventArgs" /> that contains the event data.</param>
        protected override void OnDockChanged(EventArgs e)
        {
            base.OnDockChanged(e);

            this.ResizeComponents();
        }

        /// <summary>
        /// Raises the <see cref="E:System.Windows.Forms.UserControl.Load" /> event.
        /// </summary>
        /// <param name="e">An <see cref="T:System.EventArgs" /> that contains the event data.</param>
        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);

            this.ResizeComponents();
        }

        /// <summary>
        /// Raises the <see cref="E:System.Windows.Forms.Control.PaddingChanged" /> event.
        /// </summary>
        /// <param name="e">An <see cref="T:System.EventArgs" /> that contains the event data.</param>
        protected override void OnPaddingChanged(EventArgs e)
        {
            base.OnPaddingChanged(e);

            this.ResizeComponents();
        }

        /// <summary>
        /// Raises the <see cref="E:Resize" /> event.
        /// </summary>
        /// <param name="e">An <see cref="T:System.EventArgs" /> that contains the event data.</param>
        protected override void OnResize(EventArgs e)
        {
            base.OnResize(e);

            this.ResizeComponents();
        }

        #endregion

        #region Public Properties

        /// <summary>
        /// Gets or sets the component color.
        /// </summary>
        /// <value>The component color.</value>
        [Category("Appearance")]
        [DefaultValue(typeof(Color), "0, 0, 0")]
        public virtual Color Color {
            get { return _color; }
            set {
                /*
         * If the color isn't solid, and ShowAlphaChannel is false
         * remove the alpha channel. Not sure if this is the best
         * place to do it, but it is a blanket fix for now
         */
                if (value.A != 255 && !this.ShowAlphaChannel) {
                    value = Color.FromArgb(255, value);
                }

                if (_color != value) {
                    _color = value;

                    if (!this.LockUpdates) {
                        this.LockUpdates = true;
                        this.HslColor = new HslColor(value);
                        this.LockUpdates = false;
                        this.UpdateFields(false);
                    } else {
                        this.OnColorChanged(EventArgs.Empty);
                    }
                }
            }
        }

        /// <summary>
        /// Gets or sets the component color as a HSL structure.
        /// </summary>
        /// <value>The component color.</value>
        [Browsable(false)]
        [DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)]
        public virtual HslColor HslColor {
            get { return _hslColor; }
            set {
                if (this.HslColor != value) {
                    _hslColor = value;

                    if (!this.LockUpdates) {
                        this.LockUpdates = true;
                        this.Color = value.ToRgbColor();
                        this.LockUpdates = false;
                        this.UpdateFields(false);
                    } else {
                        this.OnColorChanged(EventArgs.Empty);
                    }
                }
            }
        }

        /// <summary>
        /// Gets or sets the orientation of the editor.
        /// </summary>
        /// <value>The orientation.</value>
        [Category("Appearance")]
        [DefaultValue(typeof(Orientation), "Vertical")]
        public virtual Orientation Orientation {
            get { return _orientation; }
            set {
                if (this.Orientation != value) {
                    _orientation = value;

                    this.OnOrientationChanged(EventArgs.Empty);
                }
            }
        }

        [Category("Behavior")]
        [DefaultValue(true)]
        public virtual bool ShowAlphaChannel {
            get { return _showAlphaChannel; }
            set {
                if (this.ShowAlphaChannel != value) {
                    _showAlphaChannel = value;

                    this.OnShowAlphaChannelChanged(EventArgs.Empty);
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

        /// <summary>
        /// Raises the <see cref="ColorChanged" /> event.
        /// </summary>
        /// <param name="e">The <see cref="EventArgs" /> instance containing the event data.</param>
        protected virtual void OnColorChanged(EventArgs e)
        {
            EventHandler handler;

            this.UpdateFields(false);

            handler = this.ColorChanged;

            if (handler != null) {
                handler(this, e);
            }
        }

        /// <summary>
        /// Raises the <see cref="OrientationChanged" /> event.
        /// </summary>
        /// <param name="e">The <see cref="EventArgs" /> instance containing the event data.</param>
        protected virtual void OnOrientationChanged(EventArgs e)
        {
            EventHandler handler;

            this.ResizeComponents();

            handler = this.OrientationChanged;

            if (handler != null) {
                handler(this, e);
            }
        }

        /// <summary>
        /// Raises the <see cref="ShowAlphaChannelChanged" /> event.
        /// </summary>
        /// <param name="e">The <see cref="EventArgs" /> instance containing the event data.</param>
        protected virtual void OnShowAlphaChannelChanged(EventArgs e)
        {
            EventHandler handler;

            this.SetControlStates();

            handler = this.ShowAlphaChannelChanged;

            if (handler != null) {
                handler(this, e);
            }
        }

        /// <summary>
        /// Resizes the editing components.
        /// </summary>
        protected virtual void ResizeComponents()
        {
            try {
                int group1HeaderLeft;
                int group1BarLeft;
                int group1EditLeft;
                int group2HeaderLeft;
                int group2BarLeft;
                int group2EditLeft;
                int barWidth;
                int editWidth;
                int top;
                int innerMargin;
                int columnWidth;
                int rowHeight;
                int labelOffset;
                int colorBarOffset;
                int editOffset;
                int hexEditOffset;

                top = this.Padding.Top;
                innerMargin = 3;
                editWidth = TextRenderer.MeasureText(new string('W', 6), this.Font).Width;
                hexEditOffset = editWidth / 2;
                rowHeight = Math.Max(Math.Max(rLabel.Height, rColorBar.Height), rNumericUpDown.Height);
                labelOffset = (rowHeight - rLabel.Height) / 2;
                colorBarOffset = (rowHeight - rColorBar.Height) / 2;
                editOffset = (rowHeight - rNumericUpDown.Height) / 2;

                switch (this.Orientation) {
                    case Orientation.Horizontal:
                        columnWidth = (this.ClientSize.Width - (this.Padding.Horizontal + innerMargin)) / 2;
                        break;
                    default:
                        columnWidth = this.ClientSize.Width - this.Padding.Horizontal;
                        break;
                }

                group1HeaderLeft = this.Padding.Left;
                group1EditLeft = columnWidth - editWidth;
                group1BarLeft = group1HeaderLeft + aLabel.Width + innerMargin;

                if (this.Orientation == Orientation.Horizontal) {
                    group2HeaderLeft = this.Padding.Left + columnWidth + innerMargin;
                    group2EditLeft = this.ClientSize.Width - (this.Padding.Right + editWidth);
                    group2BarLeft = group2HeaderLeft + aLabel.Width + innerMargin;
                } else {
                    group2HeaderLeft = group1HeaderLeft;
                    group2EditLeft = group1EditLeft;
                    group2BarLeft = group1BarLeft;
                }

                barWidth = group1EditLeft - (group1BarLeft + innerMargin);

                // RGB header
                rgbHeaderLabel.SetBounds(group1HeaderLeft, top + labelOffset, 0, 0, BoundsSpecified.Location);
                top += rowHeight + innerMargin;

                // R row
                rLabel.SetBounds(group1HeaderLeft, top + labelOffset, 0, 0, BoundsSpecified.Location);
                rColorBar.SetBounds(group1BarLeft, top + colorBarOffset, barWidth, 0, BoundsSpecified.Location | BoundsSpecified.Width);
                rNumericUpDown.SetBounds(group1EditLeft + editOffset, top, editWidth, 0, BoundsSpecified.Location | BoundsSpecified.Width);
                top += rowHeight + innerMargin;

                // G row
                gLabel.SetBounds(group1HeaderLeft, top + labelOffset, 0, 0, BoundsSpecified.Location);
                gColorBar.SetBounds(group1BarLeft, top + colorBarOffset, barWidth, 0, BoundsSpecified.Location | BoundsSpecified.Width);
                gNumericUpDown.SetBounds(group1EditLeft + editOffset, top, editWidth, 0, BoundsSpecified.Location | BoundsSpecified.Width);
                top += rowHeight + innerMargin;

                // B row
                bLabel.SetBounds(group1HeaderLeft, top + labelOffset, 0, 0, BoundsSpecified.Location);
                bColorBar.SetBounds(group1BarLeft, top + colorBarOffset, barWidth, 0, BoundsSpecified.Location | BoundsSpecified.Width);
                bNumericUpDown.SetBounds(group1EditLeft + editOffset, top, editWidth, 0, BoundsSpecified.Location | BoundsSpecified.Width);
                top += rowHeight + innerMargin;

                // Hex row
                hexLabel.SetBounds(group1HeaderLeft, top + labelOffset, 0, 0, BoundsSpecified.Location);
                hexTextBox.SetBounds(group1EditLeft - hexEditOffset, top + colorBarOffset, hexEditOffset + editWidth, 0, BoundsSpecified.Location | BoundsSpecified.Width);
                top += rowHeight + innerMargin;

                // reset top
                if (this.Orientation == Orientation.Horizontal) {
                    top = this.Padding.Top;
                }

                // HSL header
                hslLabel.SetBounds(group2HeaderLeft, top + labelOffset, 0, 0, BoundsSpecified.Location);
                top += rowHeight + innerMargin;

                // H row
                hLabel.SetBounds(group2HeaderLeft, top + labelOffset, 0, 0, BoundsSpecified.Location);
                hColorBar.SetBounds(group2BarLeft, top + colorBarOffset, barWidth, 0, BoundsSpecified.Location | BoundsSpecified.Width);
                hNumericUpDown.SetBounds(group2EditLeft, top + editOffset, editWidth, 0, BoundsSpecified.Location | BoundsSpecified.Width);
                top += rowHeight + innerMargin;

                // S row
                sLabel.SetBounds(group2HeaderLeft, top + labelOffset, 0, 0, BoundsSpecified.Location);
                sColorBar.SetBounds(group2BarLeft, top + colorBarOffset, barWidth, 0, BoundsSpecified.Location | BoundsSpecified.Width);
                sNumericUpDown.SetBounds(group2EditLeft, top + editOffset, editWidth, 0, BoundsSpecified.Location | BoundsSpecified.Width);
                top += rowHeight + innerMargin;

                // L row
                lLabel.SetBounds(group2HeaderLeft, top + labelOffset, 0, 0, BoundsSpecified.Location);
                lColorBar.SetBounds(group2BarLeft, top + colorBarOffset, barWidth, 0, BoundsSpecified.Location | BoundsSpecified.Width);
                lNumericUpDown.SetBounds(group2EditLeft, top + editOffset, editWidth, 0, BoundsSpecified.Location | BoundsSpecified.Width);
                top += rowHeight + innerMargin;

                // A row
                aLabel.SetBounds(group2HeaderLeft, top + labelOffset, 0, 0, BoundsSpecified.Location);
                aColorBar.SetBounds(group2BarLeft, top + colorBarOffset, barWidth, 0, BoundsSpecified.Location | BoundsSpecified.Width);
                aNumericUpDown.SetBounds(group2EditLeft, top + editOffset, editWidth, 0, BoundsSpecified.Location | BoundsSpecified.Width);
                
                hexTextBox.Location = new Point(aNumericUpDown.Location.X, hexTextBox.Location.Y);
                hexTextBox.Width = aNumericUpDown.Width;
            }
        // ReSharper disable EmptyGeneralCatchClause
      catch
 {        // ReSharper restore EmptyGeneralCatchClause
                // ignore errors
            }
        }

        /// <summary>
        /// Updates the editing field values.
        /// </summary>
        /// <param name="userAction">if set to <c>true</c> the update is due to user interaction.</param>
        protected virtual void UpdateFields(bool userAction)
        {
            if (!this.LockUpdates) {
                try {
                    this.LockUpdates = true;

                    // RGB
                    if (!(userAction && rNumericUpDown.Focused)) {
                        rNumericUpDown.Value = this.Color.R;
                    }
                    if (!(userAction && gNumericUpDown.Focused)) {
                        gNumericUpDown.Value = this.Color.G;
                    }
                    if (!(userAction && bNumericUpDown.Focused)) {
                        bNumericUpDown.Value = this.Color.B;
                    }
                    rColorBar.Value = this.Color.R;
                    rColorBar.Color = this.Color;
                    gColorBar.Value = this.Color.G;
                    gColorBar.Color = this.Color;
                    bColorBar.Value = this.Color.B;
                    bColorBar.Color = this.Color;

                    // HTML
                    if (!(userAction && hexTextBox.Focused)) {
                        hexTextBox.Text = string.Format("{0:X2}{1:X2}{2:X2}", this.Color.R, this.Color.G, this.Color.B);
                    }

                    // HSL
                    if (!(userAction && hNumericUpDown.Focused)) {
                        hNumericUpDown.Value = (int)this.HslColor.H;
                    }
                    if (!(userAction && sNumericUpDown.Focused)) {
                        sNumericUpDown.Value = (int)(this.HslColor.S * 100);
                    }
                    if (!(userAction && lNumericUpDown.Focused)) {
                        lNumericUpDown.Value = (int)(this.HslColor.L * 100);
                    }
                    hColorBar.Value = (int)this.HslColor.H;
                    sColorBar.Color = this.Color;
                    sColorBar.Value = (int)(this.HslColor.S * 100);
                    lColorBar.Color = this.Color;
                    lColorBar.Value = (int)(this.HslColor.L * 100);

                    // Alpha
                    if (!(userAction && aNumericUpDown.Focused)) {
                        aNumericUpDown.Value = this.Color.A;
                    }
                    aColorBar.Color = this.Color;
                    aColorBar.Value = this.Color.A;
                } finally {
                    this.LockUpdates = false;
                }
            }
        }

        #endregion

        #region Private Members

        private string AddSpaces(string text)
        {
            string result;

            //http://stackoverflow.com/a/272929/148962

            if (!string.IsNullOrEmpty(text)) {
                StringBuilder newText;

                newText = new StringBuilder(text.Length * 2);
                newText.Append(text[0]);
                for (int i = 1; i < text.Length; i++) {
                    if (char.IsUpper(text[i]) && text[i - 1] != ' ') {
                        newText.Append(' ');
                    }
                    newText.Append(text[i]);
                }

                result = newText.ToString();
            } else {
                result = null;
            }

            return result;
        }

        private void SetControlStates()
        {
            aLabel.Visible = this.ShowAlphaChannel;
            aColorBar.Visible = this.ShowAlphaChannel;
            aNumericUpDown.Visible = this.ShowAlphaChannel;
        }

        #endregion

        #region Event Handlers

        /// <summary>
        /// Change handler for editing components.
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        private void ValueChangedHandler(object sender, EventArgs e)
        {
            if (!this.LockUpdates) {
                bool useHsl;
                bool useRgb;
                bool useNamed;

                useHsl = false;
                useRgb = false;
                useNamed = false;

                this.LockUpdates = true;

                if (sender == hexTextBox) {
                    string text;

                    text = hexTextBox.Text;
                    if (text.StartsWith("#")) {
                        text = text.Substring(1);
                    }

                    if (text.Length == 6 || text.Length == 8) {
                        try {
                            Color color;

                            color = ColorTranslator.FromHtml("#" + text);
                            aNumericUpDown.Value = color.A;
                            rNumericUpDown.Value = color.R;
                            bNumericUpDown.Value = color.B;
                            gNumericUpDown.Value = color.G;

                            useRgb = true;
                        }
              // ReSharper disable EmptyGeneralCatchClause
            catch {
                        }
                        // ReSharper restore EmptyGeneralCatchClause
                    } else {
                        useNamed = true;
                    }
                } else if (sender == aColorBar || sender == rColorBar || sender == gColorBar || sender == bColorBar) {
                    aNumericUpDown.Value = (int)aColorBar.Value;
                    rNumericUpDown.Value = (int)rColorBar.Value;
                    gNumericUpDown.Value = (int)gColorBar.Value;
                    bNumericUpDown.Value = (int)bColorBar.Value;

                    useRgb = true;
                } else if (sender == aNumericUpDown || sender == rNumericUpDown || sender == gNumericUpDown || sender == bNumericUpDown) {
                    useRgb = true;
                } else if (sender == hColorBar || sender == lColorBar || sender == sColorBar) {
                    hNumericUpDown.Value = (int)hColorBar.Value;
                    sNumericUpDown.Value = (int)sColorBar.Value;
                    lNumericUpDown.Value = (int)lColorBar.Value;

                    useHsl = true;
                } else if (sender == hNumericUpDown || sender == sNumericUpDown || sender == lNumericUpDown) {
                    useHsl = true;
                }

                if (useRgb || useNamed) {
                    Color color;

                    color = useNamed ? Color.FromName(hexTextBox.Text) : Color.FromArgb((int)aNumericUpDown.Value, (int)rNumericUpDown.Value, (int)gNumericUpDown.Value, (int)bNumericUpDown.Value);

                    this.Color = color;
                    this.HslColor = new HslColor(color);
                } else if (useHsl) {
                    HslColor color;

                    color = new HslColor((int)aNumericUpDown.Value, (double)hNumericUpDown.Value, (double)sNumericUpDown.Value / 100, (double)lNumericUpDown.Value / 100);
                    this.HslColor = color;
                    this.Color = color.ToRgbColor();
                }

                this.LockUpdates = false;
                this.UpdateFields(true);
            }
        }
        void HexTextBoxTextChanged(object sender, EventArgs e)
        {
            var text = hexTextBox.Text;
            if (!this.LockUpdates && (text.Length == 8 || text.Length == 6)) {
                this.LockUpdates = true;
                try {
                    Color color;

                    color = ColorTranslator.FromHtml("#" + text);
                    aNumericUpDown.Value = color.A;
                    rNumericUpDown.Value = color.R;
                    bNumericUpDown.Value = color.B;
                    gNumericUpDown.Value = color.G;
                    
                    this.Color = color;
                }
                catch {
                }
            }
            
            this.LockUpdates = false;
            this.UpdateFields(true);
        }

        #endregion
    }
}
