package com.hdfs;

import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class HdfsMain {
	private static Logger logger = LoggerFactory.getLogger(HdfsLoader.class);

	public static void main(String[] args) {
		if(args.length < 1) {
			System.err.println("Usage : CONF_FILE_PATH");
			return;
		}
		
		String confpath = args[0];

		Properties properties = new Properties();
		
		try {
			FileInputStream fis = new FileInputStream(confpath);
			properties.load(new BufferedInputStream(fis));
		} 
		catch ( IOException e ) {
			logger.error("properties load error {}", e.getMessage());
			return;
		}
		
		try {
			HdfsLoader hdfsLoader = new HdfsLoader(properties);
			hdfsLoader.putToHdfs();
		} 
		catch (Exception e) {
			logger.error("hdfs loader start error {}", e.getMessage());
		}
	}

}
