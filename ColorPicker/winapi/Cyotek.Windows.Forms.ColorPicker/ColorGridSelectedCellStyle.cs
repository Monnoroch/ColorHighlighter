namespace Cyotek.Windows.Forms
{
  // Cyotek Color Picker controls library
  // Copyright © 2013-2015 Cyotek Ltd.
  // http://cyotek.com/blog/tag/colorpicker

  // Licensed under the MIT License. See license.txt for the full text.

  // If you use this code in your applications, donations or attribution are welcome

  /// <summary>
  /// Determines how the selected cell in a <see cref="ColorGrid" /> control is rendered.
  /// </summary>
  public enum ColorGridSelectedCellStyle
  {
    /// <summary>
    /// The selected cell is drawn no differently to any other cell.
    /// </summary>
    None,

    /// <summary>
    /// The selected cell displays a basic outline and focus rectangle.
    /// </summary>
    Standard,

    /// <summary>
    /// The selected cell is displayed larger than other cells
    /// </summary>
    Zoomed
  }
}
