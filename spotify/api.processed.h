# 1 "spotify/api.h"
# 1 "<command-line>"
# 1 "spotify/api.h"
# 50 "spotify/api.h"
typedef uint64_t sp_uint64;





typedef unsigned char bool;


typedef unsigned char byte;







typedef struct sp_session sp_session;
typedef struct sp_track sp_track;
typedef struct sp_album sp_album;
typedef struct sp_artist sp_artist;
typedef struct sp_artistbrowse sp_artistbrowse;
typedef struct sp_albumbrowse sp_albumbrowse;
typedef struct sp_toplistbrowse sp_toplistbrowse;
typedef struct sp_search sp_search;
typedef struct sp_link sp_link;
typedef struct sp_image sp_image;
typedef struct sp_user sp_user;
typedef struct sp_playlist sp_playlist;
typedef struct sp_playlistcontainer sp_playlistcontainer;
typedef struct sp_inbox sp_inbox;
# 95 "spotify/api.h"
typedef enum sp_error {
  SP_ERROR_OK = 0,
  SP_ERROR_BAD_API_VERSION = 1,
  SP_ERROR_API_INITIALIZATION_FAILED = 2,
  SP_ERROR_TRACK_NOT_PLAYABLE = 3,
  SP_ERROR_BAD_APPLICATION_KEY = 5,
  SP_ERROR_BAD_USERNAME_OR_PASSWORD = 6,
  SP_ERROR_USER_BANNED = 7,
  SP_ERROR_UNABLE_TO_CONTACT_SERVER = 8,
  SP_ERROR_CLIENT_TOO_OLD = 9,
  SP_ERROR_OTHER_PERMANENT = 10,
  SP_ERROR_BAD_USER_AGENT = 11,
  SP_ERROR_MISSING_CALLBACK = 12,
  SP_ERROR_INVALID_INDATA = 13,
  SP_ERROR_INDEX_OUT_OF_RANGE = 14,
  SP_ERROR_USER_NEEDS_PREMIUM = 15,
  SP_ERROR_OTHER_TRANSIENT = 16,
  SP_ERROR_IS_LOADING = 17,
  SP_ERROR_NO_STREAM_AVAILABLE = 18,
  SP_ERROR_PERMISSION_DENIED = 19,
  SP_ERROR_INBOX_IS_FULL = 20,
  SP_ERROR_NO_CACHE = 21,
  SP_ERROR_NO_SUCH_USER = 22,
  SP_ERROR_NO_CREDENTIALS = 23,
  SP_ERROR_NETWORK_DISABLED = 24,
  SP_ERROR_INVALID_DEVICE_ID = 25,
  SP_ERROR_CANT_OPEN_TRACE_FILE = 26,
  SP_ERROR_APPLICATION_BANNED = 27,
  SP_ERROR_OFFLINE_TOO_MANY_TRACKS = 31,
  SP_ERROR_OFFLINE_DISK_CACHE = 32,
  SP_ERROR_OFFLINE_EXPIRED = 33,
  SP_ERROR_OFFLINE_NOT_ALLOWED = 34,
  SP_ERROR_OFFLINE_LICENSE_LOST = 35,
  SP_ERROR_OFFLINE_LICENSE_ERROR = 36,
  SP_ERROR_LASTFM_AUTH_ERROR = 39,
  SP_ERROR_INVALID_ARGUMENT = 40,
  SP_ERROR_SYSTEM_FAILURE = 41,
} sp_error;







const char* sp_error_message(sp_error error);
# 170 "spotify/api.h"
typedef enum sp_connectionstate {
  SP_CONNECTION_STATE_LOGGED_OUT = 0,
  SP_CONNECTION_STATE_LOGGED_IN = 1,
  SP_CONNECTION_STATE_DISCONNECTED = 2,
  SP_CONNECTION_STATE_UNDEFINED = 3,
  SP_CONNECTION_STATE_OFFLINE = 4
} sp_connectionstate;





typedef enum sp_sampletype {
  SP_SAMPLETYPE_INT16_NATIVE_ENDIAN = 0,
} sp_sampletype;




typedef struct sp_audioformat {
  sp_sampletype sample_type;
  int sample_rate;
  int channels;
} sp_audioformat;




typedef enum sp_bitrate {
  SP_BITRATE_160k = 0,
  SP_BITRATE_320k = 1,
  SP_BITRATE_96k = 2,
} sp_bitrate;




typedef enum sp_playlist_type {
  SP_PLAYLIST_TYPE_PLAYLIST = 0,
  SP_PLAYLIST_TYPE_START_FOLDER = 1,
  SP_PLAYLIST_TYPE_END_FOLDER = 2,
  SP_PLAYLIST_TYPE_PLACEHOLDER = 3,
} sp_playlist_type;






typedef enum sp_search_type {
  SP_SEARCH_STANDARD = 0,
  SP_SEARCH_SUGGEST = 1,
} sp_search_type;




typedef enum sp_playlist_offline_status {
  SP_PLAYLIST_OFFLINE_STATUS_NO = 0,
  SP_PLAYLIST_OFFLINE_STATUS_YES = 1,
  SP_PLAYLIST_OFFLINE_STATUS_DOWNLOADING = 2,
  SP_PLAYLIST_OFFLINE_STATUS_WAITING = 3,
} sp_playlist_offline_status;




typedef enum sp_availability {
  SP_TRACK_AVAILABILITY_UNAVAILABLE = 0,
  SP_TRACK_AVAILABILITY_AVAILABLE = 1,
  SP_TRACK_AVAILABILITY_NOT_STREAMABLE = 2,
  SP_TRACK_AVAILABILITY_BANNED_BY_ARTIST = 3,
} sp_track_availability;




typedef enum sp_track_offline_status {
  SP_TRACK_OFFLINE_NO = 0,
  SP_TRACK_OFFLINE_WAITING = 1,
  SP_TRACK_OFFLINE_DOWNLOADING = 2,
  SP_TRACK_OFFLINE_DONE = 3,
  SP_TRACK_OFFLINE_ERROR = 4,
  SP_TRACK_OFFLINE_DONE_EXPIRED = 5,
  SP_TRACK_OFFLINE_LIMIT_EXCEEDED = 6,
  SP_TRACK_OFFLINE_DONE_RESYNC = 7,
} sp_track_offline_status;




typedef enum sp_image_size {
  SP_IMAGE_SIZE_NORMAL = 0,
  SP_IMAGE_SIZE_SMALL = 1,
  SP_IMAGE_SIZE_LARGE = 2,
} sp_image_size;




typedef struct sp_audio_buffer_stats {
  int samples;
  int stutter;
} sp_audio_buffer_stats;




typedef struct sp_subscribers {
  unsigned int count;
  char *subscribers[1];
} sp_subscribers;





typedef enum sp_connection_type {
  SP_CONNECTION_TYPE_UNKNOWN = 0,
  SP_CONNECTION_TYPE_NONE = 1,
  SP_CONNECTION_TYPE_MOBILE = 2,
  SP_CONNECTION_TYPE_MOBILE_ROAMING = 3,
  SP_CONNECTION_TYPE_WIFI = 4,
  SP_CONNECTION_TYPE_WIRED = 5,
} sp_connection_type;







typedef enum sp_connection_rules {
  SP_CONNECTION_RULE_NETWORK = 0x1,
  SP_CONNECTION_RULE_NETWORK_IF_ROAMING = 0x2,
  SP_CONNECTION_RULE_ALLOW_SYNC_OVER_MOBILE = 0x4,
  SP_CONNECTION_RULE_ALLOW_SYNC_OVER_WIFI = 0x8,
} sp_connection_rules;





typedef enum sp_artistbrowse_type {
  SP_ARTISTBROWSE_FULL,

  SP_ARTISTBROWSE_NO_TRACKS,


  SP_ARTISTBROWSE_NO_ALBUMS,





} sp_artistbrowse_type;

typedef enum sp_social_provider {
  SP_SOCIAL_PROVIDER_SPOTIFY,
  SP_SOCIAL_PROVIDER_FACEBOOK,
  SP_SOCIAL_PROVIDER_LASTFM,
} sp_social_provider;

typedef enum sp_scrobbling_state {
  SP_SCROBBLING_STATE_USE_GLOBAL_SETTING = 0,
  SP_SCROBBLING_STATE_LOCAL_ENABLED = 1,
  SP_SCROBBLING_STATE_LOCAL_DISABLED = 2,
  SP_SCROBBLING_STATE_GLOBAL_ENABLED = 3,
  SP_SCROBBLING_STATE_GLOBAL_DISABLED = 4,
} sp_scrobbling_state;





typedef struct sp_offline_sync_status {




  int queued_tracks;
  sp_uint64 queued_bytes;





  int done_tracks;
  sp_uint64 done_bytes;





  int copied_tracks;
  sp_uint64 copied_bytes;





  int willnotcopy_tracks;





  int error_tracks;




  bool syncing;

} sp_offline_sync_status;
# 393 "spotify/api.h"
typedef struct sp_session_callbacks {
# 409 "spotify/api.h"
  void ( *logged_in)(sp_session *session, sp_error error);
# 418 "spotify/api.h"
  void ( *logged_out)(sp_session *session);
# 427 "spotify/api.h"
  void ( *metadata_updated)(sp_session *session);
# 446 "spotify/api.h"
  void ( *connection_error)(sp_session *session, sp_error error);
# 457 "spotify/api.h"
  void ( *message_to_user)(sp_session *session, const char *message);
# 470 "spotify/api.h"
  void ( *notify_main_thread)(sp_session *session);
# 491 "spotify/api.h"
  int ( *music_delivery)(sp_session *session, const sp_audioformat *format, const void *frames, int num_frames);
# 509 "spotify/api.h"
  void ( *play_token_lost)(sp_session *session);







  void ( *log_message)(sp_session *session, const char *data);
# 527 "spotify/api.h"
  void ( *end_of_track)(sp_session *session);
# 541 "spotify/api.h"
  void ( *streaming_error)(sp_session *session, sp_error error);






  void ( *userinfo_updated)(sp_session *session);
# 561 "spotify/api.h"
  void ( *start_playback)(sp_session *session);
# 575 "spotify/api.h"
  void ( *stop_playback)(sp_session *session);
# 587 "spotify/api.h"
  void ( *get_audio_buffer_stats)(sp_session *session, sp_audio_buffer_stats *stats);






  void ( *offline_status_updated)(sp_session *session);
# 603 "spotify/api.h"
  void ( *offline_error)(sp_session *session, sp_error error);
# 614 "spotify/api.h"
  void ( *credentials_blob_updated)(sp_session *session, const char *blob);






  void ( *connectionstate_updated)(sp_session *session);
# 640 "spotify/api.h"
  ...;







  void ( *scrobble_error)(sp_session *session, sp_error error);







  void ( *private_session_mode_changed)(sp_session *session, bool is_private);

} sp_session_callbacks;




typedef struct sp_session_config {
  int api_version;
  const char *cache_location;



  const char *settings_location;





  const void *application_key;
  size_t application_key_size;
  const char *user_agent;



  const sp_session_callbacks *callbacks;
  void *userdata;




  bool compress_playlists;






  bool dont_save_metadata_for_playlists;





  bool initially_unload_playlists;






  const char *device_id;





  const char *proxy;



  const char *proxy_username;



  const char *proxy_password;
# 731 "spotify/api.h"
  ...;




  const char *tracefile;

} sp_session_config;
# 761 "spotify/api.h"
sp_error sp_session_create(const sp_session_config *config, sp_session **sess);
# 770 "spotify/api.h"
sp_error sp_session_release(sp_session *sess);
# 794 "spotify/api.h"
sp_error sp_session_login(sp_session *session, const char *username, const char *password, bool remember_me, const char *blob);
# 807 "spotify/api.h"
sp_error sp_session_relogin(sp_session *session);
# 823 "spotify/api.h"
int sp_session_remembered_user(sp_session *session, char *buffer, size_t buffer_size);
# 833 "spotify/api.h"
const char * sp_session_user_name(sp_session *session);
# 843 "spotify/api.h"
sp_error sp_session_forget_me(sp_session *session);
# 853 "spotify/api.h"
sp_user * sp_session_user(sp_session *session);
# 865 "spotify/api.h"
sp_error sp_session_logout(sp_session *session);
# 943 "spotify/api.h"
sp_error sp_session_flush_caches(sp_session *session);
# 952 "spotify/api.h"
sp_connectionstate sp_session_connectionstate(sp_session *session);
# 961 "spotify/api.h"
void * sp_session_userdata(sp_session *session);
# 973 "spotify/api.h"
sp_error sp_session_set_cache_size(sp_session *session, size_t size);
# 983 "spotify/api.h"
sp_error sp_session_process_events(sp_session *session, int *next_timeout);
# 1001 "spotify/api.h"
sp_error sp_session_player_load(sp_session *session, sp_track *track);
# 1011 "spotify/api.h"
sp_error sp_session_player_seek(sp_session *session, int offset);
# 1021 "spotify/api.h"
sp_error sp_session_player_play(sp_session *session, bool play);
# 1033 "spotify/api.h"
sp_error sp_session_player_unload(sp_session *session);
# 1051 "spotify/api.h"
sp_error sp_session_player_prefetch(sp_session *session, sp_track *track);
# 1060 "spotify/api.h"
sp_playlistcontainer * sp_session_playlistcontainer(sp_session *session);
# 1071 "spotify/api.h"
sp_playlist * sp_session_inbox_create(sp_session *session);
# 1082 "spotify/api.h"
sp_playlist * sp_session_starred_create(sp_session *session);
# 1094 "spotify/api.h"
sp_playlist * sp_session_starred_for_user_create(sp_session *session, const char *canonical_username);
# 1122 "spotify/api.h"
sp_playlistcontainer * sp_session_publishedcontainer_for_user_create(sp_session *session, const char *canonical_username);
# 1134 "spotify/api.h"
sp_error sp_session_preferred_bitrate(sp_session *session, sp_bitrate bitrate);
# 1147 "spotify/api.h"
sp_error sp_session_preferred_offline_bitrate(sp_session *session, sp_bitrate bitrate, bool allow_resync);
# 1158 "spotify/api.h"
bool sp_session_get_volume_normalization(sp_session *session);
# 1169 "spotify/api.h"
sp_error sp_session_set_volume_normalization(sp_session *session, bool on);
# 1183 "spotify/api.h"
sp_error sp_session_set_private_session(sp_session *session, bool enabled);
# 1192 "spotify/api.h"
bool sp_session_is_private_session(sp_session *session);
# 1207 "spotify/api.h"
sp_error sp_session_set_scrobbling(sp_session *session, sp_social_provider provider, sp_scrobbling_state state);
# 1219 "spotify/api.h"
sp_error sp_session_is_scrobbling(sp_session *session, sp_social_provider provider, sp_scrobbling_state* state);
# 1233 "spotify/api.h"
  sp_error sp_session_is_scrobbling_possible(sp_session *session, sp_social_provider provider, bool* out);
# 1254 "spotify/api.h"
sp_error sp_session_set_social_credentials(sp_session *session, sp_social_provider provider, const char* username, const char* password);
# 1269 "spotify/api.h"
sp_error sp_session_set_connection_type(sp_session *session, sp_connection_type type);
# 1285 "spotify/api.h"
sp_error sp_session_set_connection_rules(sp_session *session, sp_connection_rules rules);
# 1297 "spotify/api.h"
int sp_offline_tracks_to_sync(sp_session *session);
# 1306 "spotify/api.h"
int sp_offline_num_playlists(sp_session *session);
# 1319 "spotify/api.h"
bool sp_offline_sync_get_status(sp_session *session, sp_offline_sync_status *status);
# 1329 "spotify/api.h"
int sp_offline_time_left(sp_session *session);
# 1339 "spotify/api.h"
int sp_session_user_country(sp_session *session);
# 1356 "spotify/api.h"
typedef enum {
  SP_LINKTYPE_INVALID = 0,
  SP_LINKTYPE_TRACK = 1,
  SP_LINKTYPE_ALBUM = 2,
  SP_LINKTYPE_ARTIST = 3,
  SP_LINKTYPE_SEARCH = 4,
  SP_LINKTYPE_PLAYLIST = 5,
  SP_LINKTYPE_PROFILE = 6,
  SP_LINKTYPE_STARRED = 7,
  SP_LINKTYPE_LOCALTRACK = 8,
  SP_LINKTYPE_IMAGE = 9,


} sp_linktype;
# 1383 "spotify/api.h"
sp_link * sp_link_create_from_string(const char *link);
# 1396 "spotify/api.h"
sp_link * sp_link_create_from_track(sp_track *track, int offset);
# 1408 "spotify/api.h"
sp_link * sp_link_create_from_album(sp_album *album);
# 1421 "spotify/api.h"
sp_link * sp_link_create_from_album_cover(sp_album *album, sp_image_size size);
# 1433 "spotify/api.h"
sp_link * sp_link_create_from_artist(sp_artist *artist);
# 1447 "spotify/api.h"
sp_link * sp_link_create_from_artist_portrait(sp_artist *artist, sp_image_size size);
# 1466 "spotify/api.h"
sp_link * sp_link_create_from_artistbrowse_portrait(sp_artistbrowse *arb, int index);
# 1479 "spotify/api.h"
sp_link * sp_link_create_from_search(sp_search *search);
# 1496 "spotify/api.h"
sp_link * sp_link_create_from_playlist(sp_playlist *playlist);
# 1508 "spotify/api.h"
sp_link * sp_link_create_from_user(sp_user *user);
# 1520 "spotify/api.h"
sp_link * sp_link_create_from_image(sp_image *image);
# 1534 "spotify/api.h"
int sp_link_as_string(sp_link *link, char *buffer, int buffer_size);
# 1543 "spotify/api.h"
sp_linktype sp_link_type(sp_link *link);
# 1553 "spotify/api.h"
sp_track * sp_link_as_track(sp_link *link);
# 1565 "spotify/api.h"
sp_track * sp_link_as_track_and_offset(sp_link *link, int *offset);
# 1575 "spotify/api.h"
sp_album * sp_link_as_album(sp_link *link);
# 1585 "spotify/api.h"
sp_artist * sp_link_as_artist(sp_link *link);
# 1596 "spotify/api.h"
sp_user * sp_link_as_user(sp_link *link);
# 1606 "spotify/api.h"
sp_error sp_link_add_ref(sp_link *link);
# 1615 "spotify/api.h"
sp_error sp_link_release(sp_link *link);
# 1635 "spotify/api.h"
bool sp_track_is_loaded(sp_track *track);
# 1648 "spotify/api.h"
sp_error sp_track_error(sp_track *track);
# 1660 "spotify/api.h"
sp_track_offline_status sp_track_offline_get_status(sp_track *track);
# 1673 "spotify/api.h"
sp_track_availability sp_track_get_availability(sp_session *session, sp_track *track);
# 1686 "spotify/api.h"
bool sp_track_is_local(sp_session *session, sp_track *track);
# 1699 "spotify/api.h"
bool sp_track_is_autolinked(sp_session *session, sp_track *track);
# 1711 "spotify/api.h"
sp_track * sp_track_get_playable(sp_session *session, sp_track *track);
# 1728 "spotify/api.h"
bool sp_track_is_placeholder(sp_track *track);
# 1742 "spotify/api.h"
bool sp_track_is_starred(sp_session *session, sp_track *track);
# 1755 "spotify/api.h"
sp_error sp_track_set_starred(sp_session *session, sp_track *const*tracks, int num_tracks, bool star);
# 1765 "spotify/api.h"
int sp_track_num_artists(sp_track *track);
# 1775 "spotify/api.h"
sp_artist * sp_track_artist(sp_track *track, int index);
# 1786 "spotify/api.h"
sp_album * sp_track_album(sp_track *track);
# 1798 "spotify/api.h"
const char * sp_track_name(sp_track *track);
# 1808 "spotify/api.h"
int sp_track_duration(sp_track *track);
# 1818 "spotify/api.h"
int sp_track_popularity(sp_track *track);
# 1829 "spotify/api.h"
int sp_track_disc(sp_track *track);
# 1840 "spotify/api.h"
int sp_track_index(sp_track *track);
# 1865 "spotify/api.h"
sp_track * sp_localtrack_create(const char *artist, const char *title, const char *album, int length);
# 1874 "spotify/api.h"
sp_error sp_track_add_ref(sp_track *track);
# 1883 "spotify/api.h"
sp_error sp_track_release(sp_track *track);
# 1897 "spotify/api.h"
typedef enum {
  SP_ALBUMTYPE_ALBUM = 0,
  SP_ALBUMTYPE_SINGLE = 1,
  SP_ALBUMTYPE_COMPILATION = 2,
  SP_ALBUMTYPE_UNKNOWN = 3,
} sp_albumtype;







bool sp_album_is_loaded(sp_album *album);
# 1923 "spotify/api.h"
bool sp_album_is_available(sp_album *album);







sp_artist * sp_album_artist(sp_album *album);
# 1945 "spotify/api.h"
const byte * sp_album_cover(sp_album *album, sp_image_size size);
# 1956 "spotify/api.h"
const char * sp_album_name(sp_album *album);
# 1965 "spotify/api.h"
int sp_album_year(sp_album *album);
# 1975 "spotify/api.h"
sp_albumtype sp_album_type(sp_album *album);
# 1985 "spotify/api.h"
sp_error sp_album_add_ref(sp_album *album);
# 1994 "spotify/api.h"
sp_error sp_album_release(sp_album *album);
# 2014 "spotify/api.h"
const char * sp_artist_name(sp_artist *artist);
# 2024 "spotify/api.h"
bool sp_artist_is_loaded(sp_artist *artist);
# 2037 "spotify/api.h"
const byte * sp_artist_portrait(sp_artist *artist, sp_image_size size);
# 2046 "spotify/api.h"
sp_error sp_artist_add_ref(sp_artist *artist);
# 2055 "spotify/api.h"
sp_error sp_artist_release(sp_artist *artist);
# 2079 "spotify/api.h"
typedef void albumbrowse_complete_cb(sp_albumbrowse *result, void *userdata);
# 2095 "spotify/api.h"
sp_albumbrowse * sp_albumbrowse_create(sp_session *session, sp_album *album, albumbrowse_complete_cb *callback, void *userdata);
# 2104 "spotify/api.h"
bool sp_albumbrowse_is_loaded(sp_albumbrowse *alb);
# 2118 "spotify/api.h"
sp_error sp_albumbrowse_error(sp_albumbrowse *alb);
# 2127 "spotify/api.h"
sp_album * sp_albumbrowse_album(sp_albumbrowse *alb);
# 2136 "spotify/api.h"
sp_artist * sp_albumbrowse_artist(sp_albumbrowse *alb);
# 2145 "spotify/api.h"
int sp_albumbrowse_num_copyrights(sp_albumbrowse *alb);
# 2157 "spotify/api.h"
const char * sp_albumbrowse_copyright(sp_albumbrowse *alb, int index);
# 2166 "spotify/api.h"
int sp_albumbrowse_num_tracks(sp_albumbrowse *alb);
# 2178 "spotify/api.h"
sp_track * sp_albumbrowse_track(sp_albumbrowse *alb, int index);
# 2189 "spotify/api.h"
const char * sp_albumbrowse_review(sp_albumbrowse *alb);
# 2199 "spotify/api.h"
int sp_albumbrowse_backend_request_duration(sp_albumbrowse *alb);
# 2209 "spotify/api.h"
sp_error sp_albumbrowse_add_ref(sp_albumbrowse *alb);
# 2218 "spotify/api.h"
sp_error sp_albumbrowse_release(sp_albumbrowse *alb);
# 2245 "spotify/api.h"
typedef void artistbrowse_complete_cb(sp_artistbrowse *result, void *userdata);
# 2262 "spotify/api.h"
sp_artistbrowse * sp_artistbrowse_create(sp_session *session, sp_artist *artist, sp_artistbrowse_type type, artistbrowse_complete_cb *callback, void *userdata);
# 2271 "spotify/api.h"
bool sp_artistbrowse_is_loaded(sp_artistbrowse *arb);
# 2284 "spotify/api.h"
sp_error sp_artistbrowse_error(sp_artistbrowse *arb);
# 2293 "spotify/api.h"
sp_artist * sp_artistbrowse_artist(sp_artistbrowse *arb);
# 2302 "spotify/api.h"
int sp_artistbrowse_num_portraits(sp_artistbrowse *arb);
# 2314 "spotify/api.h"
const byte * sp_artistbrowse_portrait(sp_artistbrowse *arb, int index);
# 2323 "spotify/api.h"
int sp_artistbrowse_num_tracks(sp_artistbrowse *arb);
# 2335 "spotify/api.h"
sp_track * sp_artistbrowse_track(sp_artistbrowse *arb, int index);
# 2346 "spotify/api.h"
int sp_artistbrowse_num_tophit_tracks(sp_artistbrowse *arb);
# 2359 "spotify/api.h"
sp_track * sp_artistbrowse_tophit_track(sp_artistbrowse *arb, int index);
# 2368 "spotify/api.h"
int sp_artistbrowse_num_albums(sp_artistbrowse *arb);
# 2380 "spotify/api.h"
sp_album * sp_artistbrowse_album(sp_artistbrowse *arb, int index);
# 2389 "spotify/api.h"
int sp_artistbrowse_num_similar_artists(sp_artistbrowse *arb);
# 2401 "spotify/api.h"
sp_artist * sp_artistbrowse_similar_artist(sp_artistbrowse *arb, int index);
# 2413 "spotify/api.h"
const char * sp_artistbrowse_biography(sp_artistbrowse *arb);
# 2423 "spotify/api.h"
int sp_artistbrowse_backend_request_duration(sp_artistbrowse *arb);
# 2433 "spotify/api.h"
sp_error sp_artistbrowse_add_ref(sp_artistbrowse *arb);
# 2442 "spotify/api.h"
sp_error sp_artistbrowse_release(sp_artistbrowse *arb);
# 2456 "spotify/api.h"
typedef enum {
  SP_IMAGE_FORMAT_UNKNOWN = -1,
  SP_IMAGE_FORMAT_JPEG = 0,
} sp_imageformat;





typedef void image_loaded_cb(sp_image *image, void *userdata);
# 2479 "spotify/api.h"
sp_image * sp_image_create(sp_session *session, const byte image_id[20]);
# 2492 "spotify/api.h"
sp_image * sp_image_create_from_link(sp_session *session, sp_link *l);
# 2506 "spotify/api.h"
sp_error sp_image_add_load_callback(sp_image *image, image_loaded_cb *callback, void *userdata);
# 2518 "spotify/api.h"
sp_error sp_image_remove_load_callback(sp_image *image, image_loaded_cb *callback, void *userdata);
# 2528 "spotify/api.h"
bool sp_image_is_loaded(sp_image *image);
# 2541 "spotify/api.h"
sp_error sp_image_error(sp_image *image);
# 2550 "spotify/api.h"
sp_imageformat sp_image_format(sp_image *image);
# 2561 "spotify/api.h"
const void * sp_image_data(sp_image *image, size_t *data_size);
# 2570 "spotify/api.h"
const byte * sp_image_image_id(sp_image *image);
# 2580 "spotify/api.h"
sp_error sp_image_add_ref(sp_image *image);
# 2589 "spotify/api.h"
sp_error sp_image_release(sp_image *image);
# 2610 "spotify/api.h"
typedef void search_complete_cb(sp_search *result, void *userdata);
# 2631 "spotify/api.h"
sp_search * sp_search_create(sp_session *session, const char *query, int track_offset, int track_count, int album_offset, int album_count, int artist_offset, int artist_count, int playlist_offset, int playlist_count, sp_search_type search_type, search_complete_cb *callback, void *userdata);
# 2640 "spotify/api.h"
bool sp_search_is_loaded(sp_search *search);
# 2653 "spotify/api.h"
sp_error sp_search_error(sp_search *search);
# 2662 "spotify/api.h"
int sp_search_num_tracks(sp_search *search);
# 2672 "spotify/api.h"
sp_track * sp_search_track(sp_search *search, int index);
# 2681 "spotify/api.h"
int sp_search_num_albums(sp_search *search);
# 2691 "spotify/api.h"
sp_album * sp_search_album(sp_search *search, int index);
# 2700 "spotify/api.h"
int sp_search_num_playlists(sp_search *search);
# 2710 "spotify/api.h"
sp_playlist * sp_search_playlist(sp_search *search, int index);
# 2720 "spotify/api.h"
const char * sp_search_playlist_name(sp_search *search, int index);
# 2730 "spotify/api.h"
const char * sp_search_playlist_uri(sp_search *search, int index);
# 2740 "spotify/api.h"
const char * sp_search_playlist_image_uri(sp_search *search, int index);
# 2749 "spotify/api.h"
int sp_search_num_artists(sp_search *search);
# 2759 "spotify/api.h"
sp_artist * sp_search_artist(sp_search *search, int index);
# 2768 "spotify/api.h"
const char * sp_search_query(sp_search *search);
# 2777 "spotify/api.h"
const char * sp_search_did_you_mean(sp_search *search);
# 2788 "spotify/api.h"
int sp_search_total_tracks(sp_search *search);
# 2799 "spotify/api.h"
int sp_search_total_albums(sp_search *search);
# 2810 "spotify/api.h"
int sp_search_total_artists(sp_search *search);
# 2821 "spotify/api.h"
int sp_search_total_playlists(sp_search *search);
# 2830 "spotify/api.h"
sp_error sp_search_add_ref(sp_search *search);
# 2839 "spotify/api.h"
sp_error sp_search_release(sp_search *search);
# 2864 "spotify/api.h"
typedef struct sp_playlist_callbacks {
# 2875 "spotify/api.h"
  void ( *tracks_added)(sp_playlist *pl, sp_track * const *tracks, int num_tracks, int position, void *userdata);
# 2885 "spotify/api.h"
  void ( *tracks_removed)(sp_playlist *pl, const int *tracks, int num_tracks, void *userdata);
# 2896 "spotify/api.h"
  void ( *tracks_moved)(sp_playlist *pl, const int *tracks, int num_tracks, int new_position, void *userdata);







  void ( *playlist_renamed)(sp_playlist *pl, void *userdata);
# 2920 "spotify/api.h"
  void ( *playlist_state_changed)(sp_playlist *pl, void *userdata);
# 2933 "spotify/api.h"
  void ( *playlist_update_in_progress)(sp_playlist *pl, bool done, void *userdata);







  void ( *playlist_metadata_updated)(sp_playlist *pl, void *userdata);
# 2952 "spotify/api.h"
  void ( *track_created_changed)(sp_playlist *pl, int position, sp_user *user, int when, void *userdata);
# 2962 "spotify/api.h"
  void ( *track_seen_changed)(sp_playlist *pl, int position, bool seen, void *userdata);
# 2971 "spotify/api.h"
  void ( *description_changed)(sp_playlist *pl, const char *desc, void *userdata);
# 2981 "spotify/api.h"
  void ( *image_changed)(sp_playlist *pl, const byte *image, void *userdata);
# 2992 "spotify/api.h"
  void ( *track_message_changed)(sp_playlist *pl, int position, const char *message, void *userdata);
# 3001 "spotify/api.h"
  void ( *subscribers_changed)(sp_playlist *pl, void *userdata);

} sp_playlist_callbacks;
# 3014 "spotify/api.h"
bool sp_playlist_is_loaded(sp_playlist *playlist);
# 3029 "spotify/api.h"
sp_error sp_playlist_add_callbacks(sp_playlist *playlist, sp_playlist_callbacks *callbacks, void *userdata);
# 3048 "spotify/api.h"
sp_error sp_playlist_remove_callbacks(sp_playlist *playlist, sp_playlist_callbacks *callbacks, void *userdata);
# 3057 "spotify/api.h"
int sp_playlist_num_tracks(sp_playlist *playlist);
# 3067 "spotify/api.h"
sp_track * sp_playlist_track(sp_playlist *playlist, int index);
# 3077 "spotify/api.h"
int sp_playlist_track_create_time(sp_playlist *playlist, int index);
# 3087 "spotify/api.h"
sp_user * sp_playlist_track_creator(sp_playlist *playlist, int index);
# 3097 "spotify/api.h"
bool sp_playlist_track_seen(sp_playlist *playlist, int index);
# 3110 "spotify/api.h"
sp_error sp_playlist_track_set_seen(sp_playlist *playlist, int index, bool seen);
# 3120 "spotify/api.h"
const char * sp_playlist_track_message(sp_playlist *playlist, int index);
# 3129 "spotify/api.h"
const char * sp_playlist_name(sp_playlist *playlist);
# 3143 "spotify/api.h"
sp_error sp_playlist_rename(sp_playlist *playlist, const char *new_name);
# 3152 "spotify/api.h"
sp_user * sp_playlist_owner(sp_playlist *playlist);
# 3163 "spotify/api.h"
bool sp_playlist_is_collaborative(sp_playlist *playlist);
# 3175 "spotify/api.h"
sp_error sp_playlist_set_collaborative(sp_playlist *playlist, bool collaborative);
# 3188 "spotify/api.h"
sp_error sp_playlist_set_autolink_tracks(sp_playlist *playlist, bool link);
# 3199 "spotify/api.h"
const char * sp_playlist_get_description(sp_playlist *playlist);
# 3211 "spotify/api.h"
bool sp_playlist_get_image(sp_playlist *playlist, byte image[20]);
# 3223 "spotify/api.h"
bool sp_playlist_has_pending_changes(sp_playlist *playlist);
# 3239 "spotify/api.h"
sp_error sp_playlist_add_tracks(sp_playlist *playlist, sp_track *const*tracks, int num_tracks, int position, sp_session *session);
# 3254 "spotify/api.h"
sp_error sp_playlist_remove_tracks(sp_playlist *playlist, const int *tracks, int num_tracks);
# 3271 "spotify/api.h"
sp_error sp_playlist_reorder_tracks(sp_playlist *playlist, const int *tracks, int num_tracks, int new_position);
# 3282 "spotify/api.h"
unsigned int sp_playlist_num_subscribers(sp_playlist *playlist);
# 3297 "spotify/api.h"
sp_subscribers * sp_playlist_subscribers(sp_playlist *playlist);
# 3306 "spotify/api.h"
sp_error sp_playlist_subscribers_free(sp_subscribers *subscribers);
# 3323 "spotify/api.h"
sp_error sp_playlist_update_subscribers(sp_session *session, sp_playlist *playlist);
# 3354 "spotify/api.h"
bool sp_playlist_is_in_ram(sp_session *session, sp_playlist *playlist);
# 3366 "spotify/api.h"
sp_error sp_playlist_set_in_ram(sp_session *session, sp_playlist *playlist, bool in_ram);
# 3377 "spotify/api.h"
sp_playlist * sp_playlist_create(sp_session *session, sp_link *link);
# 3389 "spotify/api.h"
sp_error sp_playlist_set_offline_mode(sp_session *session, sp_playlist *playlist, bool offline);
# 3403 "spotify/api.h"
sp_playlist_offline_status sp_playlist_get_offline_status(sp_session *session, sp_playlist *playlist);
# 3416 "spotify/api.h"
int sp_playlist_get_offline_download_completed(sp_session *session, sp_playlist *playlist);
# 3425 "spotify/api.h"
sp_error sp_playlist_add_ref(sp_playlist *playlist);
# 3434 "spotify/api.h"
sp_error sp_playlist_release(sp_playlist *playlist);
# 3444 "spotify/api.h"
typedef struct sp_playlistcontainer_callbacks {
# 3453 "spotify/api.h"
  void ( *playlist_added)(sp_playlistcontainer *pc, sp_playlist *playlist, int position, void *userdata);
# 3464 "spotify/api.h"
  void ( *playlist_removed)(sp_playlistcontainer *pc, sp_playlist *playlist, int position, void *userdata);
# 3476 "spotify/api.h"
  void ( *playlist_moved)(sp_playlistcontainer *pc, sp_playlist *playlist, int position, int new_position, void *userdata);







  void ( *container_loaded)(sp_playlistcontainer *pc, void *userdata);
} sp_playlistcontainer_callbacks;
# 3505 "spotify/api.h"
sp_error sp_playlistcontainer_add_callbacks(sp_playlistcontainer *pc, sp_playlistcontainer_callbacks *callbacks, void *userdata);
# 3520 "spotify/api.h"
sp_error sp_playlistcontainer_remove_callbacks(sp_playlistcontainer *pc, sp_playlistcontainer_callbacks *callbacks, void *userdata);
# 3531 "spotify/api.h"
int sp_playlistcontainer_num_playlists(sp_playlistcontainer *pc);
# 3542 "spotify/api.h"
bool sp_playlistcontainer_is_loaded(sp_playlistcontainer *pc);
# 3554 "spotify/api.h"
sp_playlist * sp_playlistcontainer_playlist(sp_playlistcontainer *pc, int index);
# 3566 "spotify/api.h"
sp_playlist_type sp_playlistcontainer_playlist_type(sp_playlistcontainer *pc, int index);
# 3583 "spotify/api.h"
sp_error sp_playlistcontainer_playlist_folder_name(sp_playlistcontainer *pc, int index, char *buffer, int buffer_size);
# 3595 "spotify/api.h"
sp_uint64 sp_playlistcontainer_playlist_folder_id(sp_playlistcontainer *pc, int index);
# 3606 "spotify/api.h"
sp_playlist * sp_playlistcontainer_add_new_playlist(sp_playlistcontainer *pc, const char *name);
# 3616 "spotify/api.h"
sp_playlist * sp_playlistcontainer_add_playlist(sp_playlistcontainer *pc, sp_link *link);
# 3628 "spotify/api.h"
sp_error sp_playlistcontainer_remove_playlist(sp_playlistcontainer *pc, int index);
# 3643 "spotify/api.h"
sp_error sp_playlistcontainer_move_playlist(sp_playlistcontainer *pc, int index, int new_position, bool dry_run);
# 3667 "spotify/api.h"
sp_error sp_playlistcontainer_add_folder(sp_playlistcontainer *pc, int index, const char *name);
# 3676 "spotify/api.h"
sp_user * sp_playlistcontainer_owner(sp_playlistcontainer *pc);
# 3686 "spotify/api.h"
sp_error sp_playlistcontainer_add_ref(sp_playlistcontainer *pc);
# 3695 "spotify/api.h"
sp_error sp_playlistcontainer_release(sp_playlistcontainer *pc);
# 3710 "spotify/api.h"
int sp_playlistcontainer_get_unseen_tracks(sp_playlistcontainer *pc, sp_playlist *playlist, sp_track **tracks, int num_tracks);
# 3719 "spotify/api.h"
int sp_playlistcontainer_clear_unseen_tracks(sp_playlistcontainer *pc, sp_playlist *playlist);
# 3733 "spotify/api.h"
typedef enum sp_relation_type {
  SP_RELATION_TYPE_UNKNOWN = 0,
  SP_RELATION_TYPE_NONE = 1,
  SP_RELATION_TYPE_UNIDIRECTIONAL = 2,
  SP_RELATION_TYPE_BIDIRECTIONAL = 3,
} sp_relation_type;
# 3749 "spotify/api.h"
const char * sp_user_canonical_name(sp_user *user);
# 3761 "spotify/api.h"
const char * sp_user_display_name(sp_user *user);
# 3771 "spotify/api.h"
bool sp_user_is_loaded(sp_user *user);
# 3781 "spotify/api.h"
sp_error sp_user_add_ref(sp_user *user);
# 3790 "spotify/api.h"
sp_error sp_user_release(sp_user *user);
# 3803 "spotify/api.h"
typedef enum {
  SP_TOPLIST_TYPE_ARTISTS = 0,
  SP_TOPLIST_TYPE_ALBUMS = 1,
  SP_TOPLIST_TYPE_TRACKS = 2,
} sp_toplisttype;
# 3822 "spotify/api.h"
typedef enum {
  SP_TOPLIST_REGION_EVERYWHERE = 0,
  SP_TOPLIST_REGION_USER = 1,
} sp_toplistregion;
# 3838 "spotify/api.h"
typedef void toplistbrowse_complete_cb(sp_toplistbrowse *result, void *userdata);
# 3857 "spotify/api.h"
sp_toplistbrowse * sp_toplistbrowse_create(sp_session *session, sp_toplisttype type, sp_toplistregion region, const char *username, toplistbrowse_complete_cb *callback, void *userdata);
# 3867 "spotify/api.h"
bool sp_toplistbrowse_is_loaded(sp_toplistbrowse *tlb);
# 3880 "spotify/api.h"
sp_error sp_toplistbrowse_error(sp_toplistbrowse *tlb);
# 3891 "spotify/api.h"
sp_error sp_toplistbrowse_add_ref(sp_toplistbrowse *tlb);
# 3900 "spotify/api.h"
sp_error sp_toplistbrowse_release(sp_toplistbrowse *tlb);
# 3909 "spotify/api.h"
int sp_toplistbrowse_num_artists(sp_toplistbrowse *tlb);
# 3919 "spotify/api.h"
sp_artist * sp_toplistbrowse_artist(sp_toplistbrowse *tlb, int index);
# 3929 "spotify/api.h"
int sp_toplistbrowse_num_albums(sp_toplistbrowse *tlb);
# 3940 "spotify/api.h"
sp_album * sp_toplistbrowse_album(sp_toplistbrowse *tlb, int index);
# 3950 "spotify/api.h"
int sp_toplistbrowse_num_tracks(sp_toplistbrowse *tlb);
# 3961 "spotify/api.h"
sp_track * sp_toplistbrowse_track(sp_toplistbrowse *tlb, int index);
# 3971 "spotify/api.h"
int sp_toplistbrowse_backend_request_duration(sp_toplistbrowse *tlb);
# 3991 "spotify/api.h"
typedef void inboxpost_complete_cb(sp_inbox *result, void *userdata);
# 4006 "spotify/api.h"
sp_inbox * sp_inbox_post_tracks(sp_session *session, const char *user, sp_track * const *tracks, int num_tracks, const char *message, inboxpost_complete_cb *callback, void *userdata);
# 4023 "spotify/api.h"
sp_error sp_inbox_error(sp_inbox *inbox);
# 4032 "spotify/api.h"
sp_error sp_inbox_add_ref(sp_inbox *inbox);
# 4041 "spotify/api.h"
sp_error sp_inbox_release(sp_inbox *inbox);
# 4051 "spotify/api.h"
const char * sp_build_id(void);
