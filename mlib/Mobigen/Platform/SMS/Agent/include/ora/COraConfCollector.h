
#ifndef __CORACONFCOLLECTOR_H__
#define __CORACONFCOLLECTOR_H__ 1

#include "CCollector.h"

/**
 * Oracle 구성 정보를 저장하기 위한 구조체
 */
typedef struct _st_oraconf {
	char 		dbname[64];
	char 		status[20];
	char		version[20];
	char		db_uptime[20];
	char		service_name[20];
	long		sga_max_size;
	int			sessions;
	int			processes;
	int			db_files;
	int			session_max_files;
	int			open_cursors;
	char		character_set[64];
	int			db_block_size;
	long		shared_pool_size;
	long		shared_pool_reserved_size;
	long		sort_area_size;
	int			dbwr_io_slaves;
	int			log_archive_mode;
}st_oraconf;

class COraConfCollector:public CCollector
{
	public:
		/** 생성자 */
		COraConfCollector();
		/** 소멸자 */
		virtual ~COraConfCollector();
		/**
		 * Oracle oraconf segment status 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();
		/**
		 *	Oracle에 SQL Query를 질의하여 결과를 얻어오는 메쏘드.
		 */
		bool collectOraData();
		/**
		 *	수집된 Oracle oraconf 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		bool collectOraVersion(st_oraconf *);
		bool collectOraParameter(st_oraconf *);
		void makeMessage();

	private:
		v_list_t *m_list;			/**< oraconf segment 정보를 저장하는 리스트 */
		st_oraconf *m_oraconf;	/**< oraconf segment 정보를 조회하기 위한 구조체 */
};

#endif /* __CORACONFCOLLECTOR_H__ */
