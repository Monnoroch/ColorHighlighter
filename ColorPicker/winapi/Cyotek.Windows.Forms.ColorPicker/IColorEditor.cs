using System;
using System.Drawing;

namespace Cyotek.Windows.Forms
{
  // Cyotek Color Picker controls library
  // Copyright © 2013-2015 Cyotek Ltd.
  // http://cyotek.com/blog/tag/colorpicker

  // Licensed under the MIT License. See license.txt for the full text.

  // If you use this code in your applications, donations or attribution are welcome

  /// <summary>
  /// Provides functionality required by color editors that are bindable
  /// </summary>
  public interface IColorEditor
  {
    #region Events

    /// <summary>
    /// Occurs when the <see cref="Color"/> property is changed.
    /// </summary>
    event EventHandler ColorChanged;

    #endregion

    #region Properties

    /// <summary>
    /// Gets or sets the component color.
    /// </summary>
    /// <value>The component color.</value>
    Color Color { get; set; }

    #endregion
  }
}
