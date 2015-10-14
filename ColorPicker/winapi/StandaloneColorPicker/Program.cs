// 2015/10/14 - 20:49

using System;
using System.Windows.Forms;
using System.Drawing;

namespace StandaloneColorPicker
{
    /// <summary>
    /// Class with program entry point.
    /// </summary>
    internal sealed class Program
    {
        /// <summary>
        /// Program entry point.
        /// </summary>
        [STAThread]
        private static void Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            var app = new Cyotek.Windows.Forms.ColorPickerDialog();
            
            if (args.Length > 0) {
                var incolor = args[0];
                System.Diagnostics.Debug.WriteLine("Inputing color: {0}", incolor);
                app.Color = ColorTranslator.FromHtml('#' + incolor.Substring(6, 2) + incolor.Substring(0, 6));
            }
            
            Application.Run(app);
            
            var color = ColorTranslator.ToHtml(app.Color);
            color += app.Color.A.ToString("X");
            
            Console.Write(app.DialogResult == DialogResult.OK ? color : "CANCEL");
            System.Diagnostics.Debug.WriteLine(color);
        }
        
    }
}
