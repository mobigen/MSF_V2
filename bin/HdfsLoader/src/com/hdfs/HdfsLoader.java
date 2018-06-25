package com.hdfs;

import java.io.File;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.Properties;
import java.util.Scanner;
import java.util.regex.Pattern;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class HdfsLoader {
	private static Logger logger = LoggerFactory.getLogger(HdfsLoader.class);
	
	private String hdfsUrl;
	private String defaultPath;
	private Configuration conf;
	private FileSystem fileSystem;
	
	public HdfsLoader(Properties properties) {
		setProperties(properties);
		connectHdfs();
		
		try {
		} 
		catch (Exception e) {
			logger.error("db connect error {}", e);
		}
	}
	
	private void setProperties(Properties properties) {
		hdfsUrl = properties.getProperty("hdfs.url");
		defaultPath = properties.getProperty("hdfs.default.path");
	}
	
	private void connectHdfs() {
		// HDFS 
		conf = new Configuration();
		conf.set("fs.defaultFS", hdfsUrl);	
		conf.set("fs.hdfs.impl", org.apache.hadoop.hdfs.DistributedFileSystem.class.getName());
		conf.set("fs.file.impl", org.apache.hadoop.fs.LocalFileSystem.class.getName());

		try {
			fileSystem = FileSystem.get(conf);
		} 
		catch ( IOException e ) {
			logger.error("hdfs connect error {}", e.getMessage());
		}
	}
	
	public void putToHdfs() {
		Scanner in = new Scanner(System.in);
		
		while ( true ) {
			String msg = in.nextLine();
			
			if ( msg.indexOf("://") < 0 ) {
				logger.info("STD IN MSG ERROR.... MSG : {}", msg);
				System.err.println(msg);
				System.err.flush();
				continue;
			}
			
			String[] splitStr = msg.split(Pattern.quote("://"));
			
			String subFolder = splitStr[0].trim();
			
			String localFilePath = splitStr[1];
			
			File localFile = new File(localFilePath);
			
			String fileName = localFile.getName();
			String dateStr	= fileName.substring(0, 8);
			String saveFile = fileName.substring(8);
			
			Path folderPath = new Path(Paths.get(defaultPath, subFolder, dateStr).toString());
			
			try {
				boolean is_exist = fileSystem.exists(folderPath);
				
				if ( !is_exist ) {
					fileSystem.mkdirs(folderPath);
				}
			}
			catch ( IOException e ) {
				logger.error("hdfs folder create error {}", e.getMessage());
			}
			
			Path localPath 	= new Path(localFilePath); 
			Path destPath	= new Path(Paths.get(defaultPath, subFolder, dateStr, saveFile).toString());
			
			try {
				// HDFS에 파일을 올린다
				// 원본 유지, HDFS에 파일이 있다면 overwirte
				fileSystem.copyFromLocalFile(false, true, localPath, destPath);
				logger.info("HDFS UPLOAD SUCCESS.... FILE PATH : {}", destPath);
			}
			catch ( IOException e ) {
				logger.error("hdfs load error {}", e.getMessage());
			}
			
			System.err.println(msg);
			System.err.flush();
		}
	}
}
