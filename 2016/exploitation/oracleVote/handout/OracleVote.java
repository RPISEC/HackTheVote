import java.io.*;
import java.lang.management.ManagementFactory;
import java.lang.reflect.*;
import java.security.*;
import java.net.*;
import java.util.*;
import java.util.zip.*;
import java.util.jar.*;
import java.util.regex.*;

public class OracleVote
{
    public static void main(String[] args) throws Exception
    {
        byte[] smartCard = null;

        emulateHeatlamp();
        setupSandbox();

        System.out.println("Welcome to OracleVote");
        System.out.println("Please insert your smart card to vote.");
        System.out.println("(We've been getting intermittent crashes since someone started growing plants in the server room, if that happens, please try again).");

        smartCard = parseSmartCard(System.in);
        if(smartCard == null) {
            return;
        }

        try {
            //Class<?> app = new ByteClassLoader(smartCard)._class;
            Class<?> app = loadJarFile(smartCard).loadClass("SmartCard");
            Method clientMain = app.getMethod("main", new Class[] {String[].class});
            clientMain.invoke(null, new Object[] {new String[] {}});
        } catch(Throwable t) {
            t.printStackTrace(System.out);
        }
    }

    private static byte[] hexToBytes(String str)
    {
        if (str.length() % 2 == 1)
            str = "0" + str;
        byte[] b = new byte[str.length() / 2];
        for (int i = 0; i < b.length; i++)
            b[i] = (byte) (Integer.parseInt(str.substring(i*2, i*2 + 2), 16) & 0xff);
        return b;
    }

    private static class ByteClassLoader extends ClassLoader
    {
        private Class _class;

        public ByteClassLoader(byte[] c)
        {
            _class = defineClass(null, c, 0, c.length);
        }
    }

    private static byte[] parseSmartCard(InputStream i) throws Exception
    {
        BufferedReader r = new BufferedReader(new InputStreamReader(i));
        StringBuilder sb = new StringBuilder();
        String line;
        while((line = r.readLine()) != null) {
            sb.append(line);
            sb.append('\n');
            if(line.equals("")) {
                break;
            }
        }
        String scText = sb.toString();
        Pattern smartCardRegex = Pattern.compile("--- BEGIN ORACLEVOTE SMARTCARD ---([0-9a-fA-F \n]*)--- END ORACLEVOTE SMARTCARD ---");
        Matcher m = smartCardRegex.matcher(scText);
        if(!m.find()) {
            System.out.println("Invalid smartcard.");
            return null;
        }
        String scHex = m.group(1).replace("\n", "").replace(" ", "");
        return hexToBytes(scHex);
    }

    private static ClassLoader loadJarFile(byte[] jar) throws Exception {
        // http://stackoverflow.com/questions/28964450/loading-a-jar-dynamically-from-memory
        final Map<String, byte[]> map = new HashMap<>();
        try(JarInputStream is=new JarInputStream(new ByteArrayInputStream(jar))) {
            for(;;) {
                JarEntry nextEntry = is.getNextJarEntry();
                if(nextEntry==null) break;
                final int est=(int)nextEntry.getSize();
                byte[] data=new byte[est>0? est: 1024];
                int real=0;
                for(int r=is.read(data); r>0; r=is.read(data, real, data.length-real))
                    if(data.length==(real+=r)) data=Arrays.copyOf(data, data.length*2);
                if(real!=data.length) data=Arrays.copyOf(data, real);
                map.put("/"+nextEntry.getName(), data);
            }
        }
        URL u=new URL("x-buffer", null, -1, "/", new URLStreamHandler() {
            protected URLConnection openConnection(URL u) throws IOException {
                final byte[] data = map.get(u.getFile());
                if(data==null) throw new FileNotFoundException(u.getFile());
                return new URLConnection(u) {
                    public void connect() throws IOException {}
                    @Override
                    public InputStream getInputStream() throws IOException {
                        return new ByteArrayInputStream(data);
                    }
                };
            }
        });
        URLClassLoader cl=new URLClassLoader(new URL[]{u});
        return cl;
    }

    private static void setupSandbox() throws Exception
    {
        Properties props = System.getProperties();
        props.setProperty("java.security.manager", "");
        props.setProperty("java.security.policy", "=onlyCreateClassLoader.policy");
        //props.setProperty("java.security.policy", "=unsafe.policy");

        Policy.getPolicy().refresh();
        System.setSecurityManager(new SecurityManager());
    }

    private static void emulateHeatlamp() throws Exception
    {
        String pid = getPid();

        ProcessBuilder bitflipper = new ProcessBuilder("./procdump", "bitflip", pid, "-t", "2"+"500"+"000"+"000", "-p", "1");
        //bitflipper.inheritIO();
        bitflipper.start();
    }

    private static String getPid() {
        String pid = ManagementFactory.getRuntimeMXBean().getName().split("@")[0];
        //System.err.format("Our pid: %s\n", pid);
        return pid;
    }
}

