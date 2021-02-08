/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package mobigen.processors.IrisLoader;

import org.apache.nifi.components.AllowableValue;
import org.apache.nifi.components.PropertyDescriptor;
import org.apache.nifi.flowfile.FlowFile;
import org.apache.nifi.annotation.behavior.ReadsAttribute;
import org.apache.nifi.annotation.behavior.ReadsAttributes;
import org.apache.nifi.annotation.behavior.WritesAttribute;
import org.apache.nifi.annotation.behavior.WritesAttributes;
import org.apache.nifi.annotation.lifecycle.OnScheduled;
import org.apache.nifi.annotation.documentation.CapabilityDescription;
import org.apache.nifi.annotation.documentation.SeeAlso;
import org.apache.nifi.annotation.documentation.Tags;
import org.apache.nifi.processor.exception.ProcessException;
import org.apache.nifi.processor.io.InputStreamCallback;
import org.apache.nifi.processor.io.OutputStreamCallback;
import org.apache.nifi.processor.io.StreamCallback;
import org.apache.nifi.processor.AbstractProcessor;
import org.apache.nifi.processor.ProcessContext;
import org.apache.nifi.processor.ProcessSession;
import org.apache.nifi.processor.ProcessorInitializationContext;
import org.apache.nifi.processor.Relationship;
import org.apache.nifi.processor.util.StandardValidators;
import org.apache.nifi.logging.ComponentLog;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Set;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
import java.text.SimpleDateFormat;
import java.sql.ResultSet;
import java.sql.SQLException;

import com.mobigen.iris.jdbc.IRISDriver;
import com.mobigen.iris.jdbc.IRISStatement;

@Tags({ "IrisLoader" })
@CapabilityDescription("IRIS Loader Connect with GetFile")
@SeeAlso({})
@ReadsAttributes({ @ReadsAttribute(attribute = "", description = "") })
@WritesAttributes({ @WritesAttribute(attribute = "", description = "") })
public class IrisLoad extends AbstractProcessor {

	public static final PropertyDescriptor IRIS_IP = new PropertyDescriptor.Builder().name("IRIS_IP").displayName("IP")
			.description("Input Iris IP").defaultValue("127.0.0.1").required(true)
			.addValidator(StandardValidators.URI_VALIDATOR).build();

	public static final PropertyDescriptor IRIS_PORT = new PropertyDescriptor.Builder().name("IRIS_PORT")
			.displayName("PORT").description("Input Iris PORT").defaultValue("5050").required(true)
			.addValidator(StandardValidators.PORT_VALIDATOR).build();

	public static final PropertyDescriptor IRIS_ID = new PropertyDescriptor.Builder().name("IRIS_ID")
			.displayName("UserID").description("Input Iris User ID").defaultValue("root").required(true)
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR).build();

	public static final PropertyDescriptor IRIS_PASS = new PropertyDescriptor.Builder().name("IRIS_PASS")
			.displayName("UserPasswrod").description("Input Iris User Password").defaultValue("").required(true)
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR).build();

	public static final PropertyDescriptor IRIS_DATABASE = new PropertyDescriptor.Builder().name("IRIS_DATABASE")
			.displayName("Database").description("Input Iris Database Name").defaultValue("root").required(true)
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR).build();

	public static final PropertyDescriptor TARGET_TABLE = new PropertyDescriptor.Builder().name("TARGET_TABLE")
			.displayName("Table Name").description("Input Iris Table Name").defaultValue("").required(true)
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR).build();

	public static final AllowableValue P_KEY_ATTRIBUTE = new AllowableValue("attribute", "FlowFile Attribute",
			"PARTITION_KEY From FlowFile Attribute");
	public static final AllowableValue P_KEY_PROPERTY = new AllowableValue("property", "Property",
			"PARTITION_KEY From Property");

	public static final PropertyDescriptor P_KEY_FROM = new PropertyDescriptor.Builder().name("P_KEY_FROM")
			.displayName("Partition Key From").description("Choice Partition Key from")
			.allowableValues(P_KEY_ATTRIBUTE, P_KEY_PROPERTY).defaultValue(P_KEY_PROPERTY.getValue()).build();

	public static final AllowableValue P_DATE_ATTRIBUTE = new AllowableValue("attribute", "FlowFile Attribute",
			"PARTITION_DATE From FlowFile Attribute");
	public static final AllowableValue P_DATE_TODAY = new AllowableValue("today", "Today",
			"PARTITION_DATE From Date of Today");

	public static final PropertyDescriptor P_DATE_FROM = new PropertyDescriptor.Builder().name("P_DATE_FROM")
			.displayName("Partition Data From").description("Choice Partition Date from")
			.allowableValues(P_DATE_ATTRIBUTE, P_DATE_TODAY).defaultValue(P_DATE_TODAY.getValue()).build();

	public static final PropertyDescriptor PARTITION_KEY_ATTRIBUTE = new PropertyDescriptor.Builder()
			.name("PARTITION_KEY_ATTRIBUTE").displayName("Partition Key Attribute")
			.description("Input Data Parition Key")
			.defaultValue(
					"${filename:substringBeforeLast('.'):substring(${filename:substringBeforeLast('.'):length():minus(1)})}")
			.expressionLanguageSupported(true).required(false).addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
			.build();

	public static final PropertyDescriptor PARTITION_DATE_ATTRIBUTE = new PropertyDescriptor.Builder()
			.name("PARTITION_DATE_ATTRIBUTE").displayName("Partition Date Attribute")
			.description("Input Data Parition Key")
			.defaultValue(
					"${filename:substringBeforeLast('_'):substring(${filename:substringBeforeLast('_'):length():minus(14)})}")
			.expressionLanguageSupported(true).required(false).addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
			.build();

	public static final PropertyDescriptor PARTITION_KEY = new PropertyDescriptor.Builder().name("PARTITION_KEY")
			.displayName("Partition Key").description("Input Data Parition Key").defaultValue("0").required(true)
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR).build();

	public static final PropertyDescriptor PARTITION_DATE = new PropertyDescriptor.Builder().name("PARTITION_DATE")
			.displayName("Partition Date Format").description("Input Data Parition Date Format")
			.defaultValue("yyyyMMdd000000").required(true).addValidator(StandardValidators.NON_EMPTY_VALIDATOR).build();

	public static final PropertyDescriptor FIELD_SEP = new PropertyDescriptor.Builder().name("FIELD_SEP")
			.displayName("Field Seperator").description("Input Field seperator of data").defaultValue("|")
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR).required(true).build();

	public static final PropertyDescriptor CONTROL_FILE = new PropertyDescriptor.Builder().name("CONTROL_FILE")
			.displayName("Control File").description("Input control file name with path").required(true)
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR).defaultValue("").build();

	public static final AllowableValue IS_DIRECT_TRUE = new AllowableValue("true", "True", "Direct");
	public static final AllowableValue IS_DIRECT_FALSE = new AllowableValue("false", "False", "Not Direct");

	public static final AllowableValue LNX_NEWLINE = new AllowableValue("\n", "\\n", "Linux Newline");
	public static final AllowableValue WND_NEWLINE = new AllowableValue("\r\n", "\\r\\n", "Windows Newline");

	public static final PropertyDescriptor RECORD_SEP = new PropertyDescriptor.Builder().name("RECORD_SEP")
			.displayName("Record Seperator").description("Record Separator").allowableValues(LNX_NEWLINE, WND_NEWLINE).defaultValue("\n").build();

	public static final PropertyDescriptor IS_DIRECT = new PropertyDescriptor.Builder().name("DIRECT")
			.description("Connect to Iris").allowableValues(IS_DIRECT_TRUE, IS_DIRECT_FALSE).defaultValue("false")
			.build();

	public static final Relationship success = new Relationship.Builder().name("success").autoTerminateDefault(true)
			.description("Connect to PutFile Processor for collect files when success").build();

	public static final Relationship failure = new Relationship.Builder().name("failure").autoTerminateDefault(true)
			.description("Connect to PutFile Processor for collect files when failure").build();

	private List<PropertyDescriptor> descriptors;

	private Set<Relationship> relationships;

	@Override
	protected void init(final ProcessorInitializationContext context) {
		final List<PropertyDescriptor> descriptors = new ArrayList<PropertyDescriptor>();
		descriptors.add(IRIS_IP);
		descriptors.add(IRIS_PORT);
		descriptors.add(IRIS_DATABASE);
		descriptors.add(IRIS_ID);
		descriptors.add(IRIS_PASS);
		descriptors.add(IS_DIRECT);
		descriptors.add(FIELD_SEP);
		descriptors.add(RECORD_SEP);
		descriptors.add(CONTROL_FILE);
		descriptors.add(TARGET_TABLE);
		descriptors.add(PARTITION_KEY);
		descriptors.add(P_KEY_FROM);
		descriptors.add(P_DATE_FROM);
		descriptors.add(PARTITION_DATE);
		descriptors.add(PARTITION_KEY_ATTRIBUTE);
		descriptors.add(PARTITION_DATE_ATTRIBUTE);

		this.descriptors = Collections.unmodifiableList(descriptors);

		final Set<Relationship> relationships = new HashSet<Relationship>();
		relationships.add(success);
		relationships.add(failure);
		this.relationships = Collections.unmodifiableSet(relationships);

	}

	@Override
	public Set<Relationship> getRelationships() {
		return this.relationships;
	}

	@Override
	public final List<PropertyDescriptor> getSupportedPropertyDescriptors() {
		return descriptors;
	}

	@OnScheduled
	public void onScheduled(final ProcessContext context) {

	}

	@Override
	public void onTrigger(final ProcessContext context, final ProcessSession session) throws ProcessException {
		ComponentLog logger = getLogger();
		FlowFile flowFile = session.get();
		if (flowFile == null) {
			return;
		}

		// TODO implement
		final StringBuffer sb = new StringBuffer();

		session.read(flowFile, new InputStreamCallback() {
			@Override
			public void process(InputStream in) throws IOException {
				sb.append(loadToIris(logger, context, session, in, flowFile));
			}
		});

		boolean is_transfer = false;

		Set<Relationship> available = context.getAvailableRelationships();
		Iterator<Relationship> relations = available.iterator();

		while (relations.hasNext()) {
			Relationship r = relations.next();
			if (sb.toString().startsWith("true")) {
				if ("success" == r.getName()) {
					session.transfer(flowFile, success);
					session.commit();
					is_transfer = true;

				}
			} else {
				if ("failure" == r.getName()) {
					session.transfer(flowFile, failure);
					session.commit();
					is_transfer = true;

				}
			}

		}

		if (!is_transfer) {
			session.remove(flowFile);
		}
	}

	private static boolean loadToIris(ComponentLog logger, final ProcessContext context, final ProcessSession session,
			InputStream inputStream, FlowFile flowFile) {

		boolean result = false;

		Connection conn = null;

		try {
			Class.forName("com.mobigen.iris.jdbc.IRISDriver");

		} catch (java.lang.ClassNotFoundException e) {
			StringWriter sw = new StringWriter();
			e.printStackTrace(new PrintWriter(sw));
			String exceptionAsString = sw.toString();
			logger.info("===========>" + exceptionAsString);
		}

		Map<String, String> properties = context.getAllProperties();

//		logger.info("===========>IRIS_IP : " + (properties.get("IRIS_IP") == null ? IRIS_IP.getDefaultValue() : properties.get("IRIS_IP")));
//		logger.info("===========>IRIS_PORT : " + (properties.get("IRIS_PORT") == null ? IRIS_PORT.getDefaultValue() : properties.get("IRIS_PORT")));
//		logger.info("===========>IRIS_DATABASE : " + (properties.get("IRIS_DATABASE") == null ? IRIS_DATABASE.getDefaultValue() : properties.get("IRIS_DATABASE")));
//		logger.info("===========>IRIS_ID : " + (properties.get("IRIS_ID") == null ? IRIS_ID.getDefaultValue() : properties.get("IRIS_ID")));
//		logger.info("===========>IRIS_PASS : " + (properties.get("IRIS_PASS") == null ? IRIS_PASS.getDefaultValue() : properties.get("IRIS_PASS")));
//		logger.info("===========>IS_DIRECT : " + (properties.get("IS_DIRECT") == null ? IS_DIRECT.getDefaultValue() : properties.get("IS_DIRECT")));
//		logger.info("===========>FIELD_SEP : "+ (properties.get("FIELD_SEP") == null ? FIELD_SEP.getDefaultValue() : properties.get("FIELD_SEP")));
//		logger.info("===========>RECORD_SEP : "+ (properties.get("RECORD_SEP") == null ? RECORD_SEP.getDefaultValue() : properties.get("RECORD_SEP")));
//		logger.info("===========>DATA_FILE : "+ (properties.get("DATA_FILE") == null ? DATA_FILE.getDefaultValue() : properties.get("DATA_FILE")));
//		logger.info("===========>CONTROL_FILE : "+ (properties.get("CONTROL_FILE") == null ? CONTROL_FILE.getDefaultValue() : properties.get("CONTROL_FILE")));
//		logger.info("===========>TARGET_TABLE : " + (properties.get("TARGET_TABLE") == null ? TARGET_TABLE.getDefaultValue() : properties.get("TARGET_TABLE")));
//		logger.info("===========>PARTITION_KEY : " + (properties.get("PARTITION_KEY") == null ? PARTITION_KEY.getDefaultValue() : properties.get("PARTITION_KEY")));
//		logger.info("===========>PARTITION_DATE : " + (properties.get("PARTITION_DATE") == null ? PARTITION_DATE.getDefaultValue() : properties.get("PARTITION_DATE")));

		String iris_ip = (properties.get("IRIS_IP") == null ? IRIS_IP.getDefaultValue() : properties.get("IRIS_IP"));
		String iris_port = (properties.get("IRIS_PORT") == null ? IRIS_PORT.getDefaultValue()
				: properties.get("IRIS_PORT"));
		String iris_database = (properties.get("IRIS_DATABASE") == null ? IRIS_DATABASE.getDefaultValue()
				: properties.get("IRIS_DATABASE"));
		String iris_id = (properties.get("IRIS_ID") == null ? IRIS_ID.getDefaultValue() : properties.get("IRIS_ID"));
		String iris_pass = (properties.get("IRIS_PASS") == null ? IRIS_PASS.getDefaultValue()
				: properties.get("IRIS_PASS"));
		String is_direct = (properties.get("IS_DIRECT") == null ? IS_DIRECT.getDefaultValue()
				: properties.get("IS_DIRECT"));
		String field_sep = (properties.get("FIELD_SEP") == null ? FIELD_SEP.getDefaultValue()
				: properties.get("FIELD_SEP"));
		String record_sep = (properties.get("RECORD_SEP") == null ? RECORD_SEP.getDefaultValue()
				: properties.get("RECORD_SEP"));
		String control_file = (properties.get("CONTROL_FILE") == null ? CONTROL_FILE.getDefaultValue()
				: properties.get("CONTROL_FILE"));
		String target_table = (properties.get("TARGET_TABLE") == null ? TARGET_TABLE.getDefaultValue()
				: properties.get("TARGET_TABLE"));
		String partition_key = (properties.get("PARTITION_KEY") == null ? PARTITION_KEY.getDefaultValue()
				: properties.get("PARTITION_KEY"));
		String partition_date_format = (properties.get("PARTITION_DATE") == null ? PARTITION_DATE.getDefaultValue()
				: properties.get("PARTITION_DATE"));
		String p_key_from = (properties.get("P_KEY_FROM") == null ? P_KEY_FROM.getDefaultValue()
				: properties.get("P_KEY_FROM"));
		String p_date_from = (properties.get("P_DATE_FROM") == null ? P_DATE_FROM.getDefaultValue()
				: properties.get("P_DATE_FROM"));

		try {

			String url = String.format("jdbc:iris://%s:%s/%s", iris_ip, iris_port, iris_database);

			Properties info = new Properties();

			info.setProperty("user", iris_id);
			info.setProperty("password", iris_pass);
			info.setProperty("direct", is_direct);

			conn = DriverManager.getConnection(url, info);

			IRISStatement stmt = (IRISStatement) conn.createStatement();

//			logger.info("===========>field_sep : " + field_sep);
//			logger.info("===========>record_sep : " + record_sep);

			stmt.SetFieldSep(field_sep);
			stmt.SetRecordSep(record_sep);

			Date now = new Date();

			SimpleDateFormat format = new SimpleDateFormat(partition_date_format);
			String table = target_table;
			String key = partition_key;
			String partition = format.format(now);
			String control_file_path = control_file;

			if (p_key_from.startsWith("attribute")) {
				key = context.getProperty(PARTITION_KEY_ATTRIBUTE).evaluateAttributeExpressions(flowFile).getValue();
			}

			if (p_date_from.startsWith("attribute")) {
				partition = context.getProperty(PARTITION_DATE_ATTRIBUTE).evaluateAttributeExpressions(flowFile)
						.getValue();
			}

//			logger.info("===========>key : " + key);
//			logger.info("===========>partition : " + partition);

//			String data_file_path = data_file;

//			File dataFile = new File(data_file_path);
//			InputStream dataInputstream = null;
//			try {
//				dataInputstream = new FileInputStream(dataFile);
//			} catch (FileNotFoundException e) {
//				// TODO Auto-generated catch block
//				e.printStackTrace();
//			}

			File controlFile = new File(control_file_path);
			InputStream controlInputstream = null;
			try {
				controlInputstream = new FileInputStream(controlFile);
			} catch (FileNotFoundException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}

			String result_str = stmt.Load(table, key, partition, controlInputstream, inputStream);

			if (result_str.startsWith("+OK")) {
				result = true;
				logger.info("===========>" + result_str);
			} else {
				result = false;
				logger.info("===========>" + result_str);
			}

			stmt.close();
			conn.close();
		} catch (SQLException e) {
			e.printStackTrace();
			StringWriter sw = new StringWriter();
			e.printStackTrace(new PrintWriter(sw));
			String exceptionAsString = sw.toString();
			logger.info("===========>" + exceptionAsString);
			result = false;
		} finally {

		}
		return result;
	}

	private static String convertStreamToString(InputStream is) {

		BufferedReader reader = new BufferedReader(new InputStreamReader(is));
		StringBuilder sb = new StringBuilder();

		String line = null;
		try {
			while ((line = reader.readLine()) != null) {
				sb.append(line + "\n");
			}
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			try {
				is.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		return sb.toString();
	}

}
