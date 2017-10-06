using System;
using System.Drawing;
using System.IO;
using System.Text;

namespace Cyotek.Windows.Forms
{
  // Cyotek Color Picker controls library
  // Copyright © 2013-2015 Cyotek Ltd.
  // http://cyotek.com/blog/tag/colorpicker

  // Licensed under the MIT License. See license.txt for the full text.

  // If you use this code in your applications, donations or attribution are welcome

  /// <summary>
  /// Serializes and deserializes color palettes into and from the Gimp palette format.
  /// </summary>
  public class GimpPaletteSerializer : PaletteSerializer
  {
    #region Overridden Properties

    /// <summary>
    /// Gets the default extension for files generated with this palette format.
    /// </summary>
    /// <value>The default extension for files generated with this palette format.</value>
    public override string DefaultExtension
    {
      get { return "gpl"; }
    }

    /// <summary>
    /// Gets a descriptive name of the palette format
    /// </summary>
    /// <value>The descriptive name of the palette format.</value>
    public override string Name
    {
      get { return "GIMP Palette"; }
    }

    #endregion

    #region Overridden Methods

    /// <summary>
    /// Determines whether this instance can read palette from data the specified stream.
    /// </summary>
    /// <param name="stream">The stream.</param>
    /// <returns><c>true</c> if this instance can read palette data from the specified stream; otherwise, <c>false</c>.</returns>
    public override bool CanReadFrom(Stream stream)
    {
      bool result;

      if (stream == null)
      {
        throw new ArgumentNullException("stream");
      }

      try
      {
        using (StreamReader reader = new StreamReader(stream))
        {
          string header;

          header = reader.ReadLine();

          result = (header == "GIMP Palette");
        }
      }
      catch
      {
        result = false;
      }

      return result;
    }

    /// <summary>
    /// Deserializes the <see cref="ColorCollection" /> contained by the specified <see cref="Stream" />.
    /// </summary>
    /// <param name="stream">The <see cref="Stream" /> that contains the palette to deserialize.</param>
    /// <returns>The <see cref="ColorCollection" /> being deserialized.</returns>
    public override ColorCollection Deserialize(Stream stream)
    {
      ColorCollection results;

      if (stream == null)
      {
        throw new ArgumentNullException("stream");
      }

      results = new ColorCollection();

      using (StreamReader reader = new StreamReader(stream))
      {
        string header;
        int swatchIndex;
        bool readingPalette;

        readingPalette = false;

        // check signature
        header = reader.ReadLine();

        if (header != "GIMP Palette")
        {
          throw new InvalidDataException("Invalid palette file");
        }

        // read the swatches
        swatchIndex = 0;

        while (!reader.EndOfStream)
        {
          string data;

          data = reader.ReadLine();

          if (!string.IsNullOrEmpty(data))
          {
            if (data[0] == '#')
            {
              // comment
              readingPalette = true;
            }
            else if (!readingPalette)
            {
              // custom attribute
            }
            else if (readingPalette)
            {
              int r;
              int g;
              int b;
              string[] parts;
              string name;

              // TODO: Optimize this a touch. Microoptimization? Maybe.

              parts = !string.IsNullOrEmpty(data) ? data.Split(new[]
                                                               {
                                                                 ' ', '\t'
                                                               }, StringSplitOptions.RemoveEmptyEntries) : new string[0];
              name = parts.Length > 3 ? string.Join(" ", parts, 3, parts.Length - 3) : null;

              if (!int.TryParse(parts[0], out r) || !int.TryParse(parts[1], out g) || !int.TryParse(parts[2], out b))
              {
                throw new InvalidDataException(string.Format("Invalid palette contents found with data '{0}'", data));
              }

              results.Add(Color.FromArgb(r, g, b));
#if USENAMEHACK
              results.SetName(swatchIndex, name);
#endif

              swatchIndex++;
            }
          }
        }
      }

      return results;
    }

    /// <summary>
    /// Serializes the specified <see cref="ColorCollection" /> and writes the palette to a file using the specified <see cref="Stream" />.
    /// </summary>
    /// <param name="stream">The <see cref="Stream" /> used to write the palette.</param>
    /// <param name="palette">The <see cref="ColorCollection" /> to serialize.</param>
    public override void Serialize(Stream stream, ColorCollection palette)
    {
      int swatchIndex;

      if (stream == null)
      {
        throw new ArgumentNullException("stream");
      }

      if (palette == null)
      {
        throw new ArgumentNullException("palette");
      }

      swatchIndex = 0;

      // TODO: Allow name and columns attributes to be specified

      using (StreamWriter writer = new StreamWriter(stream, Encoding.ASCII))
      {
        writer.WriteLine("GIMP Palette");
        writer.WriteLine("Name: ");
        writer.WriteLine("Columns: 8");
        writer.WriteLine("#");

        foreach (Color color in palette)
        {
          writer.Write("{0,-3} ", color.R);
          writer.Write("{0,-3} ", color.G);
          writer.Write("{0,-3} ", color.B);
#if USENAMEHACK
          writer.Write(palette.GetName(swatchIndex));
#else
          if (color.IsNamedColor)
          {
            writer.Write(color.Name);
          }
          else
          {
            writer.Write("#{0:X2}{1:X2}{2:X2} Swatch {3}", color.R, color.G, color.B, swatchIndex);
          }
#endif
          writer.WriteLine();

          swatchIndex++;
        }
      }
    }

    #endregion
  }
}
