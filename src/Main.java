import cn.localhost01.seal.SealUtil;
import cn.localhost01.seal.configuration.SealCircle;
import cn.localhost01.seal.configuration.SealConfiguration;
import cn.localhost01.seal.configuration.SealFont;
import com.sun.org.apache.xpath.internal.operations.Bool;

import java.awt.*;
import java.io.*;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.List;

public class Main {

public static void main(String[] args) throws Exception {
    String root = ".";
    // 生成指定类型的印章
    for(String type:new ArrayList<String>(){{
        add("Circle");//圆形章
        add("Oval");//椭圆章
//            add("Person");//方形私人章
    }}){
        String filepath = new String();
        if(type=="Person"){
            // 存放所有文本信息
            filepath =".\\tools\\privateInfo.csv";
        }else {
            filepath =".\\tools\\publicInfo.csv";
        }
        // 遍历所有公司名称
        for(String company:getListFromFile(filepath)){

            List<String> sealType = new ArrayList<String>(){{
                add("财务专用章");
                add("发票品检部");
                add("合同专用章");
                add("名称专用章");
                add("审定专用章");
                add("法定代表人章");
                add("质检专用章");
                add("业务受理章");
            }};

            // 所有文字信息
            HashMap<String, HashMap<String, String>> confInfo = new HashMap<String, HashMap<String, String>>(){{
                List<Boolean> hidden = new ArrayList<Boolean>(){{
                    if(type=="Circle"){
                        add(true);
                        add(true);
                        Boolean flag = Integer.parseInt(getRandom(1))%2==0;
                        add(flag);
                        add(!flag);}
                    if(type=="Oval"){
                        Boolean flag = Integer.parseInt(getRandom(1))%2==0;
                        add(true);
                        add(flag);
                        add(true);
                        add(!flag);}
                }};
                if(hidden.get(0))   put("mainFont",new HashMap<String, String>(){{
                    put("Text",company);//company
                    String size = new String();
                    put("Bold","false");
                    if(type=="Circle"){
                        size = String.valueOf(new Double(
                                0.06*Math.pow(company.length(),2)-3.39*Math.pow(company.length(),1)+68.55*Math.pow(company.length(),0)).intValue());
                        put("Margin","7");

                    }
                    if(type=="Oval"){
                        size = String.valueOf(new Double(-0.52*company.length()+31.98).intValue());
                        put("Margin","5");
                        String space =String.valueOf(new Double(-0.52*company.length()+31.98-10));
                        put("Space",space);
                    }
                    put("Size",size);
                    put("Font","宋体");
                }});
                if(hidden.get(1))   put("centerFont",new HashMap<String, String>(){{
                    put("Font","宋体");

                    if(type=="Circle"){
                        put("Text","★");
                        put("Size","50");
                        put("Bold","true");
                    }
                    if(type=="Oval"){
                        put("Text",getRandom(15));
                        put("Size","23");
                        put("Bold","false");
                        put("Margin","0");
                        put("Space","12.0");
                    }

                }});
                // 副标题或印章编码随机出现
                if(hidden.get(2))   put("titleFont",new HashMap<String, String>(){{
                    put("Font","宋体");
                    put("Bold","false");
                    put("Space","10.0");
                    // 随机选取章类别
                    put("Text",sealType.get( (int) (Math.random()* sealType.size())));

                    if(type=="Circle"){
                        put("Size","35");
                        put("Margin","82");
                    }
                    if(type=="Oval"){
                        put("Size","23");
                        put("Margin","28");
                    }
                }});
                if(hidden.get(3))   put("viceFont",new HashMap<String, String>(){{
                    put("Text",getRandom(13));
                    put("Size","20");
                    put("Font","宋体");
                    put("Bold","false");
                    put("Margin","-3");

                    if(type=="Circle") {
                        put("Space","16.0");
                    }
                    if(type=="Oval") {
                        put("Space","7.0");
                    }
                }});
            }};
            // 印章圆圈信息：外圈、内圈、中心圈
            HashMap<String,List<Integer>> circleInfo = new HashMap<String,List<Integer>>(){{
                List<Boolean> hidden = new ArrayList<Boolean>(){{
                    if(type=="Circle"){
                        add(true);
                        Boolean flag = Integer.parseInt(getRandom(1))%2==0;
                        add(flag);
                        add(false);}
                    if(type=="Oval"){
                        add(true);
                        add(Integer.parseInt(getRandom(1))%2==0);
                        add(Integer.parseInt(getRandom(1))%2==0);}
                }};
                if(type=="Oval"){
                    if(hidden.get(0)) put("BorderCircle",Arrays.asList(4,140,100));
                    if(hidden.get(1)) put("BorderInnerCircle",Arrays.asList(1,135,95));
                    if(hidden.get(2)) put("InnerCircle",Arrays.asList(2,100,60));
                }
                if(type=="Circle"){
                    if(hidden.get(0)) put("BorderCircle",Arrays.asList(5,140,140));
                    if(hidden.get(1)) put("BorderInnerCircle",Arrays.asList(1,135,135));
                    if(hidden.get(2)) put("InnerCircle",Arrays.asList(2,100,100));
                }
            }};
            // 印章信息：大小、颜色、图片位置、标签位置、印章类型
            HashMap<String,String> sealInfo = new HashMap<String,String>(){{

                File folder = new File(Paths.get(root, "tools",type,"image").toString());
                if (!folder.exists() && !folder.isDirectory())  folder.mkdirs();

                Path pngFile = Paths.get(folder.toString(),company+"_"+type+".png");//company
                Path labelFile = Paths.get(root, "tools",type,"SealInfo.csv");
                put("ImgPath",pngFile.toString());      // 图片路径
                put("ImageSize","300");                 // 图片大小
                put("BackgroudColor","red");            // 背景颜色
                put("LabelPath",labelFile.toString());  // 标签文件
                put("Type",type);//Person or Public // 印章类型
            }};
            //生成印章
            sealGeneral(confInfo,circleInfo,sealInfo);
        }
    }
}

    public static void sealGeneral(HashMap<String, HashMap<String, String>> confInfo,
                                   HashMap<String,List<Integer>> circleInfo,
                                   HashMap<String,String> sealInfo) throws Exception {
        //印章基本配置
        SealConfiguration configuration = new SealConfiguration();
        List<String> labelInfo = new ArrayList<String>();
        // 设置所有的字体
        for (String key : confInfo.keySet()) {
            SealFont font = new SealFont();
            Map<String,String> tempMap = confInfo.get(key);
            // 获取每种标题的字体信息
            for(String k:tempMap.keySet()){
                switch (k){
                    case "Text":
                        font.setFontText(tempMap.get("Text"));
                        labelInfo.add(tempMap.get("Text"));
                        break;
                    case "Font":
                        font.setFontFamily(tempMap.get("Font"));
                        break;
                    case "Margin":
                        font.setMarginSize(Integer.parseInt(tempMap.get("Margin")));//边界距离
                        break;
                    case "Size":
                        font.setFontSize(Integer.parseInt(tempMap.get("Size")));
                        break;
                    case "Space":
                        font.setFontSpace(Double.valueOf(tempMap.get("Space")));
                        break;
                    case "Bold":
                        font.setBold(Boolean.parseBoolean(tempMap.get("Margin")));
                        break;
                    default:
                        break;
                }
            }
            // 匹配对应的标题文字信息
            switch (key){
                case "titleFont" :
                    configuration.setTitleFont(font);
                    break;
                case "centerFont" :
                    configuration.setCenterFont(font);
                    break;
                case "viceFont" :
                    configuration.setViceFont(font);
                    break;
                case "mainFont" :
                    configuration.setMainFont(font);
                default:
                    break;
            }
        }
        writeFile(labelInfo,sealInfo.get("LabelPath"));

        /************ 图片大小 **************/
        configuration.setImageSize(Integer.parseInt(sealInfo.get("ImageSize")));

        /************ 背景颜色 **************/
        configuration.setBackgroudColor(Color.RED);

        //设置圆圈
        for (String key:circleInfo.keySet()){
            List<Integer> info = circleInfo.get(key);
            switch (key){
                case "BorderCircle":
                    configuration.setBorderCircle(new SealCircle(info.get(0), info.get(1), info.get(2)));
                    break;
                case "BorderInnerCircle":
                    configuration.setBorderInnerCircle(new SealCircle(info.get(0), info.get(1), info.get(2)));
                    break;
                case "InnerCircle":
                    configuration.setInnerCircle(new SealCircle(info.get(0), info.get(1), info.get(2)));
                    break;
                default:
                    break;
            }
        }

        String type =sealInfo.get("Type");
        if(type=="Oval" || type=="Circle"){
            //生成公章
            SealUtil.buildAndStoreSeal(configuration, sealInfo.get("ImgPath"));
        }else if(type == "Person"){
            // 个人章
            SealFont font = new SealFont();
        font.setFontSize(120).setBold(true).setFontText("诸葛");
        SealUtil.buildAndStorePersonSeal(Integer.parseInt(sealInfo.get("ImageSize")), 16, font, "印", sealInfo.get("ImgPath"));
        }
    }
    // 从文件中获取公司名称
    public static List<String> getListFromFile(String filepath) {
        List<String> strList = new ArrayList<String>();
        File file = new File(filepath);
        InputStreamReader read = null;
        BufferedReader reader = null;
        try {
            read = new InputStreamReader(new FileInputStream(file),"GBK");
            reader = new BufferedReader(read);
            String line;
            while ((line = reader.readLine()) != null) {
                strList.add(line);
            }
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (read != null) {
                try {
                    read.close();
                } catch (IOException e) {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
            }
            if (reader != null) {
                try {
                    reader.close();
                } catch (IOException e) {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
            }

        }
        return strList;
    }


    public static String getRandom(int length){
        String val = "";
        Random random = new Random();
        for (int i = 0; i < length; i++) {
            val += String.valueOf(random.nextInt(10));
        }
        return val;
    }

    public static void writeFile(List<String> list,String filePath) {
        try{
            File file = new File(filePath);
            FileOutputStream fos = null;
            if(!file.exists()){
                file.createNewFile();//如果文件不存在，就创建该文件
                fos = new FileOutputStream(file);//首次写入获取
            }else{
                //如果文件已存在，那么就在文件末尾追加写入
                fos = new FileOutputStream(file,true);//这里构造方法多了一个参数true,表示在文件末尾追加写入
            }

            OutputStreamWriter osw = new OutputStreamWriter(fos, "UTF-8");//指定以UTF-8格式写入文件

            //遍历list
            for(String l : list){
                osw.write(l+",");
                //每写入一个Map就换一行
            }
            osw.write("\n");
            //写入完成关闭流
            osw.close();
        }catch (Exception e) {
            e.printStackTrace();
        }

    }

}
