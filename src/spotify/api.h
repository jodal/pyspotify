/*
 * Copyright (c) 2006-2009 Spotify Ltd
 *
 * The terms of use for this and related files can be read in
 * the associated LICENSE file, usually stored in share/doc/libspotify/LICENSE.
 */

/**
 * @file   api.h    Public API for libspotify
 *
 * @note   All input strings are expected to be in UTF-8
 * @note   All output strings are in UTF-8.
 *
 * @note   All usernames are valid XMPP nodeprep identifiers:
 *         http://tools.ietf.org/html/rfc3920#appendix-A
 *         If you need to store user data, we strongly advise you
 *         to use the canonical form of the username.
 */

#ifndef PUBLIC_API_H
#define PUBLIC_API_H

#ifdef __cplusplus
extern "C" {
#endif

#ifndef SP_CALLCONV
#ifdef _WIN32
#define SP_CALLCONV __stdcall
#else
#define SP_CALLCONV
#endif
#endif

#ifndef SP_LIBEXPORT
#ifdef _WIN32
#define SP_LIBEXPORT(x) x __stdcall
#else
#define SP_LIBEXPORT(x) x
#endif
#endif

/* Includes */
#include <stddef.h>

/* General types */

#ifndef __cplusplus
typedef unsigned char bool;
#endif

typedef unsigned char byte;

#include <stddef.h>

/**
 * @defgroup types Spotify types & structs
 *
 * @{
 */

typedef struct sp_session sp_session; ///< Representation of a session
typedef struct sp_track sp_track; ///< A track handle
typedef struct sp_album sp_album; ///< An album handle
typedef struct sp_artist sp_artist; ///< An artist handle
typedef struct sp_artistbrowse sp_artistbrowse; ///< A handle to an artist browse result
typedef struct sp_albumbrowse sp_albumbrowse; ///< A handle to an album browse result
typedef struct sp_search sp_search; ///< A handle to a search result
typedef struct sp_link sp_link; ///< A handle to the libspotify internal representation of a URI
typedef struct sp_image sp_image; ///< A handle to an image
typedef struct sp_user sp_user; ///< A handle to a user
typedef struct sp_playlist sp_playlist; ///< A playlist handle
typedef struct sp_playlistcontainer sp_playlistcontainer; ///< A playlist container (playlist containing other playlists) handle

/** @} */

/**
 * @defgroup error Error Handling
 *
 * All functions in libspotify use the same set of error codes. Most of them return
 * an error code, and let the result of the operation be stored in an out-parameter.
 *
 * @{
 */

/**
 * Error codes returned by various functions
 */
typedef enum sp_error {
	SP_ERROR_OK                        = 0,  ///< No errors encountered
	SP_ERROR_BAD_API_VERSION           = 1,  ///< The library version targeted does not match the one you claim you support
	SP_ERROR_API_INITIALIZATION_FAILED = 2,  ///< Initialization of library failed - are cache locations etc. valid?
	SP_ERROR_TRACK_NOT_PLAYABLE        = 3,  ///< The track specified for playing cannot be played
	SP_ERROR_RESOURCE_NOT_LOADED       = 4,  ///< One or several of the supplied resources is not yet loaded
	SP_ERROR_BAD_APPLICATION_KEY       = 5,  ///< The application key is invalid
	SP_ERROR_BAD_USERNAME_OR_PASSWORD  = 6,  ///< Login failed because of bad username and/or password
	SP_ERROR_USER_BANNED               = 7,  ///< The specified username is banned
	SP_ERROR_UNABLE_TO_CONTACT_SERVER  = 8,  ///< Cannot connect to the Spotify backend system
	SP_ERROR_CLIENT_TOO_OLD            = 9,  ///< Client is too old, library will need to be updated
	SP_ERROR_OTHER_PERMAMENT           = 10, ///< Some other error occured, and it is permanent (e.g. trying to relogin will not help)
	SP_ERROR_BAD_USER_AGENT            = 11, ///< The user agent string is invalid or too long
	SP_ERROR_MISSING_CALLBACK          = 12, ///< No valid callback registered to handle events
	SP_ERROR_INVALID_INDATA            = 13, ///< Input data was either missing or invalid
	SP_ERROR_INDEX_OUT_OF_RANGE        = 14, ///< Index out of range
	SP_ERROR_USER_NEEDS_PREMIUM        = 15, ///< The specified user needs a premium account
	SP_ERROR_OTHER_TRANSIENT           = 16, ///< A transient error occured.
	SP_ERROR_IS_LOADING                = 17, ///< The resource is currently loading
} sp_error;

/**
 * Convert a numeric libspotify error code to a text string
 *
 * Here is a snippet from \c session_ready.c:
 * @dontinclude session_ready.c
 * @skip sp_session_logout
 * @until }
 *
 * @param[in]   error   The error code to lookup
 */
SP_LIBEXPORT(const char*) sp_error_message(sp_error error);

/** @} */


/**
 * @defgroup session Session handling
 *
 * The concept of a session is fundamental for all communication with the Spotify ecosystem - it is the
 * object responsible for communicating with the Spotify service. You will need to instantiate a
 * session that then can be used to request artist information, perform searches etc.
 *
 * @{
 */

/**
 * Current version of the application interface, that is, the API described by this file.
 *
 * This value should be set in the sp_session_config struct passed to sp_session_init().
 *
 * If an (upgraded) library is no longer compatible with this version the error #SP_ERROR_BAD_API_VERSION will be
 * returned from sp_session_init(). Future versions of the library will provide you with some kind of mechanism
 * to request an updated version of the library.
 */
#define SPOTIFY_API_VERSION 2

/**
 * Describes the current state of the connection
 */
typedef enum sp_connectionstate {
	SP_CONNECTION_STATE_LOGGED_OUT   = 0, ///< User not yet logged in
	SP_CONNECTION_STATE_LOGGED_IN    = 1, ///< Logged in against a Spotify access point
	SP_CONNECTION_STATE_DISCONNECTED = 2, ///< Was logged in, but has now been disconnected
	SP_CONNECTION_STATE_UNDEFINED    = 3, ///< The connection state is undefined
} sp_connectionstate;


/**
 * Sample type descriptor
 */
typedef enum sp_sampletype {
	SP_SAMPLETYPE_INT16_NATIVE_ENDIAN = 0, ///< 16-bit signed integer samples
} sp_sampletype;

/**
 * Audio format descriptor
 */
typedef struct sp_audioformat {
	sp_sampletype sample_type;   ///< Sample type enum,
	int sample_rate;             ///< Audio sample rate, in samples per second.
	int channels;                ///< Number of channels. Currently 1 or 2.
} sp_audioformat;


/**
 * Session callbacks
 *
 * Registered when you create a session.
 * If some callbacks should not be of interest, set them to NULL.
 */
typedef struct sp_session_callbacks {

	/**
	 * Called when login has been processed and was successful
	 *
	 * @param[in]  session    Session
	 * @param[in]  error      Error code ::sp_error
	 */
	void (SP_CALLCONV *logged_in)(sp_session *session, sp_error error);

	/**
	 * Called when logout has been processed. Either called explicitly
	 * if you initialize a logout operation, or implicitly if there
	 * is a permanent connection error
	 *
	 * @param[in]  session    Session
	 */
	void (SP_CALLCONV *logged_out)(sp_session *session);

	/**
	 * Called whenever metadata has been updated
	 *
	 * If you have metadata cached outside of libspotify, you should purge
	 * your caches and fetch new versions.
	 *
	 * @param[in]  session    Session
	 */
	void (SP_CALLCONV *metadata_updated)(sp_session *session);

	/**
	 * Called when there is a connection error, and the library has problems
	 * reconnecting to the Spotify service. Could be called multiple times (as
	 * long as the problem is present)
	 *
	 *
	 * @param[in]  session    Session
	 * @param[in]  error      Status code ::sp_error
	 */
	void (SP_CALLCONV *connection_error)(sp_session *session, sp_error error);

	/**
	 * Called when the access point wants to display a message to the user
	 *
	 * In the desktop client, these are shown in a blueish toolbar just below the
	 * search box.
	 *
	 * @param[in]  session    Session
	 * @param[in]  message    String in UTF-8 format.
	 */
	void (SP_CALLCONV *message_to_user)(sp_session *session, const char *message);

	/**
	 * Called when processing needs to take place on the main thread.
	 *
	 * You need to call sp_session_process_events() in the main thread to get
	 * libspotify to do more work. Failure to do so may cause request timeouts,
	 * or a lost connection.
	 *
	 * @param[in]  session    Session
	 *
	 * @note This function is called from an internal session thread - you need to have proper synchronization!
	 */
	void (SP_CALLCONV *notify_main_thread)(sp_session *session);

	/**
	 * Called when there is decompressed audio data available.
	 *
	 * @param[in]  session    Session
	 * @param[in]  format     Audio format descriptor sp_audioformat
	 * @param[in]  frames     Points to raw PCM data as described by \p format
	 * @param[in]  num_frames Number of available samples in \p frames.
	 *                        If this is 0, a discontinuity has occured (such as after a seek). The application
	 *                        should flush its audio fifos, etc.
	 *
	 * @return                Number of frames consumed.
	 *                        This value can be used to rate limit the output from the library if your
	 *                        output buffers are saturated. The library will retry delivery in about 100ms.
	 *
	 * @note This function is called from an internal session thread - you need to have proper synchronization!
	 *
	 * @note This function must never block. If your output buffers are full you must return 0 to signal
	 *       that the library should retry delivery in a short while.
	 */
	int (SP_CALLCONV *music_delivery)(sp_session *session, const sp_audioformat *format, const void *frames, int num_frames);

	/**
	 * Music has been paused because only one account may play music at the same time.
	 *
	 * @param[in]  session    Session
	 */
	void (SP_CALLCONV *play_token_lost)(sp_session *session);

	/**
	 * Logging callback.
	 *
	 * @param[in]  session    Session
	 * @param[in]  data       Log data
	 */
	void (SP_CALLCONV *log_message)(sp_session *session, const char *data);

	/**
	 * End of track. Called when the currently played track has reached its end.
	 *
	 * @param[in]  session    Session
	 */
	void (SP_CALLCONV *end_of_track)(sp_session *session);
} sp_session_callbacks;

/**
 * Session config
 */
typedef struct sp_session_config {
	int api_version;                       ///< The version of the Spotify API your application is compiled with. Set to #SPOTIFY_API_VERSION
	const char *cache_location;            ///< The location where Spotify will write cache files
	const char *settings_location;         ///< The location where Spotify will write settings files
	const void *application_key;           ///< Your application key
	size_t application_key_size;           ///< The size of the application key in bytes
	const char *user_agent;                ///< "User-Agent" for your application - max 255 characters long
	const sp_session_callbacks *callbacks; ///< Delivery callbacks for session events, or NULL if you are not interested in any callbacks (not recommended!)
	void *userdata;                        ///< User supplied data for your application
} sp_session_config;

/**
 * Initialize a session. The session returned will be initialized, but you will need
 * to log in before you can perform any other operation
 *
 * In the future, this will be renamed to sp_session_create() and will have a
 * corresponding sp_session_release() function.
 *
 * Here is a snippet from \c session.c:
 * @dontinclude session.c
 * @skip config.api_version
 * @until }
 *
 * @param[in]   config    The configuration to use for the session
 * @param[out]  sess      If successful, a new session - otherwise NULL
 *
 * @return                Error code ::sp_error
 */
SP_LIBEXPORT(sp_error) sp_session_init(const sp_session_config *config, sp_session **sess);

/**
 * Logs in the specified username/password combo. This initiates the download in the background.
 * A callback is called when login is complete
 *
 * Here is a snippet from \c session.c:
 * @dontinclude session.c
 * @skip sp_session_login
 * @until }
 *
 * @param[in]   session    Your session object
 * @param[in]   username   The username to log in
 * @param[in]   password   The password for the specified username
 *
 * @return                 Result of the operation
 */
SP_LIBEXPORT(sp_error) sp_session_login(sp_session *session, const char *username, const char *password);

/**
 * Fetches the currently logged in user
 *
 * @param[in]   session    Your session object
 *
 * @return                 The logged in user (or NULL if not logged in)
 */
SP_LIBEXPORT(sp_user *) sp_session_user(sp_session *session);

/**
 * Logs out the currently logged in user
 *
 * Always call this before terminating the application and libspotify is currently
 * logged in. Otherwise, the settings and cache may be lost.
 *
 * Here is a snippet from \c session_ready.c:
 * @dontinclude session_ready.c
 * @skip sp_session_logout
 * @until }
 *
 * @param[in]   session    Your session object
 *
 * @return                 Result of the operation
 */
SP_LIBEXPORT(sp_error) sp_session_logout(sp_session *session);

/**
 * The connection state of the specified session.
 *
 * @param[in]   session    Your session object
 *
 * @return                 The connection state - see the sp_connectionstate enum for possible values
 */
SP_LIBEXPORT(sp_connectionstate) sp_session_connectionstate(sp_session *session);

/**
 * The userdata associated with the session
 *
 * @param[in]   session    Your session object
 *
 * @return                 The userdata that was passed in on session creation
 */
SP_LIBEXPORT(void *) sp_session_userdata(sp_session *session);

/**
 * Make the specified session process any pending events
 *
 * Here is a snippet from \c session.c:
 * @dontinclude session.c
 * @skip static void loop
 * @until }
 * @until }
 *
 * @param[in]   session         Your session object
 * @param[out]  next_timeout    Stores the time (in milliseconds) until you should call this function again
 */
SP_LIBEXPORT(void) sp_session_process_events(sp_session *session, int *next_timeout);

/**
 * Loads the specified track
 *
 * After successfully loading the track, you have the option of running
 * sp_session_player_play() directly, or using sp_session_player_seek() first.
 * When this call returns, the track will have been loaded, unless an error occurred.
 *
 * @param[in]   session    Your session object
 * @param[in]   track      The track to be loaded
 *
 * @return                 The result of the operation - see the ::sp_error enum for possible values
 */
SP_LIBEXPORT(sp_error) sp_session_player_load(sp_session *session, sp_track *track);

/**
 * Seek to position in the currently loaded track
 *
 * @param[in]   session    Your session object
 * @param[in]   offset     Track position, in milliseconds.
 *
 * @return                 The result of the operation - see the ::sp_error enum for possible values
 */
SP_LIBEXPORT(sp_error) sp_session_player_seek(sp_session *session, int offset);

/**
 * Play or pause the currently loaded track
 *
 * @param[in]   session    Your session object
 * @param[in]   play       If set to true, playback will occur. If set to false, the playback will be paused.
 *
 * @return                 The result of the operation - see the ::sp_error enum for possible values
 */
SP_LIBEXPORT(sp_error) sp_session_player_play(sp_session *session, bool play);

/**
 * Stops the currently playing track
 *
 * This frees some resources held by libspotify to identify the currently
 * playing track.
 *
 * @param[in]   session    Your session object
 *
 */
SP_LIBEXPORT(void) sp_session_player_unload(sp_session *session);

/**
 * Returns the playlist container for the currently logged in user.
 *
 * @param[in]   session    Your session object
 *
 * @return                 Playlist container object, NULL if not logged in
 */
SP_LIBEXPORT(sp_playlistcontainer *) sp_session_playlistcontainer(sp_session *session);

/** @} */


/**
 * @defgroup link Links (Spotify URIs)
 *
 * These functions handle links to Spotify entities in a way that allows you to
 * not care about the textual representation of the link.
 * @{
 */

/**
 * Link types
 */
typedef enum {
	SP_LINKTYPE_INVALID  = 0, ///< Link type not valid - default until the library has parsed the link, or when parsing failed
	SP_LINKTYPE_TRACK    = 1, ///< Link type is track
	SP_LINKTYPE_ALBUM    = 2, ///< Link type is album
	SP_LINKTYPE_ARTIST   = 3, ///< Link type is artist
	SP_LINKTYPE_SEARCH   = 4, ///< Link type is search
	SP_LINKTYPE_PLAYLIST = 5, ///< Link type is playlist
} sp_linktype;

/**
 * Create a Spotify link given a string
 *
 * Here is a snippet from \c link.c:
 * @dontinclude link.c
 * @skip sp_link_create_from_string
 * @until sp_link_release
 *
 * @param[in]   link       A string representation of a Spotify link
 *
 * @return                 A link representation of the given string representation.
 *                         If the link could not be parsed, this function returns NULL.
 *
 * @note You need to release the link when you are done with it.
 * @see sp_link_type()
 * @see sp_link_release()
 */
SP_LIBEXPORT(sp_link *) sp_link_create_from_string(const char *link);

/**
 * Generates a link object from a track
 *
 * @param[in]   track        A track object
 * @param[in]   offset       Offset in track in ms.
 *
 * @return                   A link representing the track
 *
 * @note You need to release the link when you are done with it.
 * @see sp_link_release()
 */
SP_LIBEXPORT(sp_link *) sp_link_create_from_track(sp_track *track, int offset);

/**
 * Create a link object from an album
 *
 * @param[in]   album      An album object
 *
 * @return                 A link representing the album
 *
 * @note You need to release the link when you are done with it.
 * @see sp_link_release()
 */
SP_LIBEXPORT(sp_link *) sp_link_create_from_album(sp_album *album);

/**
 * Creates a link object from an artist
 *
 * @param[in]   artist     An artist object
 *
 * @return                 A link object representing the artist
 *
 * @note You need to release the link when you are done with it.
 * @see sp_link_release()
 */
SP_LIBEXPORT(sp_link *) sp_link_create_from_artist(sp_artist *artist);

/**
 * Generate a link object representing the current search
 *
 * @param[in]  search       Search object
 *
 * @return                  A link representing the search
 *
 * @note You need to release the link when you are done with it.
 * @see sp_link_release()
 */
SP_LIBEXPORT(sp_link *) sp_link_create_from_search(sp_search *search);

/**
 * Create a link object representing the given playlist
 *
 * @param[in]  playlist       Playlist object
 *
 * @return                    A link representing the playlist
 *
 * @note You need to release the link when you are done with it.
 * @see sp_link_release()
 */
SP_LIBEXPORT(sp_link *) sp_link_create_from_playlist(sp_playlist *playlist);

/**
 * Create a string representation of the given Spotify link
 *
 * Here is a snippet from \c link.c:
 * @dontinclude link.c
 * @skip print_link
 * @until }
 * @until }
 * @until }
 *
 * @param[in]   link         The Spotify link whose string representation you are interested in
 * @param[out]  buffer       The buffer to hold the string representation of link
 * @param[in]   buffer_size  The max size of the buffer that will hold the string representation
 *                           The resulting string is guaranteed to always be null terminated if
 *                           buffer_size > 0
 *
 * @return                   The number of characters in the string representation of the link. If this
 *                           value is greater or equal than \p buffer_size, output was truncated.
 */
SP_LIBEXPORT(int) sp_link_as_string(sp_link *link, char *buffer, int buffer_size);

/**
 * The link type of the specified link
 *
 * Here is a snippet from \c link.c:
 * @dontinclude link.c
 * @skip get_link_type_label
 * @until }
 * @until }
 *
 * @param[in]   link       The Spotify link whose type you are interested in
 *
 * @return                 The link type of the specified link - see the sp_linktype enum for possible values
 */
SP_LIBEXPORT(sp_linktype) sp_link_type(sp_link *link);

/**
 * The track representation for the given link
 *
 * @param[in]   link       The Spotify link whose track you are interested in
 *
 * @return                 The track representation of the given track link
 *                         If the link is not of track type then NULL is returned.
 */
SP_LIBEXPORT(sp_track *) sp_link_as_track(sp_link *link);

/**
 * The album representation for the given link
 *
 * @param[in]   link       The Spotify link whose album you are interested in
 *
 * @return                 The album representation of the given album link
 *                         If the link is not of album type then NULL is returned
 */
SP_LIBEXPORT(sp_album *) sp_link_as_album(sp_link *link);

/**
 * The artist representation for the given link
 *
 * @param[in]   link       The Spotify link whose artist you are interested in
 *
 * @return                 The artist representation of the given link
 *                         If the link is not of artist type then NULL is returned
 */
SP_LIBEXPORT(sp_artist *) sp_link_as_artist(sp_link *link);


/**
 * Increase the reference count of a link
 *
 * @param[in]   link       The link object
 */
SP_LIBEXPORT(void) sp_link_add_ref(sp_link *link);

/**
 * Decrease the reference count of a link
 *
 * @param[in]   link       The link object
 */
SP_LIBEXPORT(void) sp_link_release(sp_link *link);

/** @} */



/**
 * @defgroup track Track subsystem
 * @{
 */

/**
 * Get load status for the specified track. If the track is not loaded yet,
 * all other functions operating on the track return default values.
 *
 * Here is a snippet from \c track.c:
 * @dontinclude track.c
 * @skip try_tracks
 * @skip sp_track_is_loaded
 * @until track = NULL
 *
 * @param[in]   track      The track whose load status you are interested in
 *
 * @return                 True if track is loaded, otherwise false
 */
SP_LIBEXPORT(bool) sp_track_is_loaded(sp_track *track);

/**
 * Return an error code associated with a track. For example if it could not load
 *
 * @param[in]   track      The track
 *
 * @return                 Error code
 */
SP_LIBEXPORT(sp_error) sp_track_error(sp_track *track);

/**
 * Return true if the track is available for playback.
 *
 * @param[in]   track      The track
 *
 * @return                 True if track is available for playback, otherwise false.
 *
 * @note The track must be loaded or this function will always return false.
 * @see sp_track_is_loaded()
 */
SP_LIBEXPORT(bool) sp_track_is_available(sp_track *track);

/**
 * The number of artists performing on the specified track
 *
 * @param[in]   track     The track whose number of participating artists you are interested in
 *
 * @return                The number of artists performing on the specified track.
 *                        If no metadata is available for the track yet, this function returns 0.
 */
SP_LIBEXPORT(int) sp_track_num_artists(sp_track *track);

/**
 * The artist matching the specified index performing on the current track.
 *
 * @param[in]   track      The track whose participating artist you are interested in
 * @param[in]   index      The index for the participating artist. Should be in the interval [0, sp_track_num_artists() - 1]
 *
 * @return                 The participating artist, or NULL if invalid index
 */
SP_LIBEXPORT(sp_artist *) sp_track_artist(sp_track *track, int index);

/**
 * The album of the specified track
 *
 * @param[in]   track      A track object
 *
 * @return                 The album of the given track. You need to increase the refcount
 *                         if you want to keep the pointer around.
 *                         If no metadata is available for the track yet, this function returns 0.
 */
SP_LIBEXPORT(sp_album *) sp_track_album(sp_track *track);

/**
 * The string representation of the specified track's name
 *
 * Here is a snippet from \c track.c:
 * @dontinclude track.c
 * @skip print_track
 * @until }
 *
 * @param[in]   track      A track object
 *
 * @return                 The string representation of the specified track's name.
 *                         Returned string is valid as long as the album object stays allocated
 *                         and no longer than the next call to sp_session_process_events()
 *                         If no metadata is available for the track yet, this function returns empty string.
 */
SP_LIBEXPORT(const char *) sp_track_name(sp_track *track);

/**
 * The duration, in milliseconds, of the specified track
 *
 * Here is a snippet from \c track.c:
 * @dontinclude track.c
 * @skip print_track
 * @until }
 *
 * @param[in]   track      A track object
 *
 * @return                 The duration of the specified track, in milliseconds
 *                         If no metadata is available for the track yet, this function returns 0.
 */
SP_LIBEXPORT(int) sp_track_duration(sp_track *track);

/**
 * Returns popularity for track
 *
 * @param[in]   track      A track object
 *
 * @return                 Popularity in range 0 to 100, 0 if undefined
 *                         If no metadata is available for the track yet, this function returns 0.
 */
SP_LIBEXPORT(int) sp_track_popularity(sp_track *track);

/**
 * Returns the disc number for a track
 *
 * @param[in]   track      A track object
 *
 * @return                 Disc index. Possible values are [1, total number of discs on album]
 *                         This function returns valid data only for tracks appearing in a browse
 *                         artist or browse album result (otherwise returns 0).
 */
SP_LIBEXPORT(int) sp_track_disc(sp_track *track);

/**
 * Returns the position of a track on its disc
 *
 * @param[in]   track      A track object
 *
 * @return                 Track position, starts at 1 (relative the corresponding disc)
 *                         This function returns valid data only for tracks appearing in a browse
 *                         artist or browse album result (otherwise returns 0).
 */
SP_LIBEXPORT(int) sp_track_index(sp_track *track);


/**
 * Increase the reference count of a track
 *
 * @param[in]   track       The track object
 */
SP_LIBEXPORT(void) sp_track_add_ref(sp_track *track);

/**
 * Decrease the reference count of a track
 *
 * @param[in]   track       The track object
 */
SP_LIBEXPORT(void) sp_track_release(sp_track *track);

/** @} */



/**
 * @defgroup album Album subsystem
 * @{
 */

/**
 * Album types
 */
typedef enum {
	SP_ALBUMTYPE_ALBUM       = 0, ///< Normal album
	SP_ALBUMTYPE_SINGLE      = 1, ///< Single
	SP_ALBUMTYPE_COMPILATION = 2, ///< Compilation
	SP_ALBUMTYPE_UNKNOWN     = 3, ///< Unknown type
} sp_albumtype;

/**
 * Check if the album object is populated with data
 *
 * @param[in]  album       Album object
 * @return True if metadata is present, false if not
 */
SP_LIBEXPORT(bool) sp_album_is_loaded(sp_album *album);


/**
 * Return true if the album is available in the current region.
 *
 * @param[in]   album      The album
 *
 * @return                 True if album is available for playback, otherwise false.
 *
 * @note The album must be loaded or this function will always return false.
 * @see sp_album_is_loaded()
 */
SP_LIBEXPORT(bool) sp_album_is_available(sp_album *album);

/**
 * Get the artist associated with the given album
 *
 * @param[in]  album       Album object
 * @return A reference to the artist. NULL if the metadata has not been loaded yet
 */
SP_LIBEXPORT(sp_artist *) sp_album_artist(sp_album *album);

/**
 * Return image ID representing the album's coverart.
 *
 * @param[in]   album      Album object
 *
 * @return                 ID byte sequence that can be passed to sp_image_create()
 *                         If the album has no image or the metadata for the album is not
 *                         loaded yet, this function returns NULL.
 *
 * @see sp_image_create
 */
SP_LIBEXPORT(const byte *) sp_album_cover(sp_album *album);

/**
 * Return name of album
 *
 * @param[in]   album      Album object
 *
 * @return                 Name of album.
 *                         Returned string is valid as long as the album object stays allocated
 *                         and no longer than the next call to sp_session_process_events()
 */
SP_LIBEXPORT(const char *) sp_album_name(sp_album *album);

/**
 * Return release year of specified album
 *
 * @param[in]   album      Album object
 *
 * @return                 Release year
 */
SP_LIBEXPORT(int) sp_album_year(sp_album *album);


/**
 * Return type of specified album
 *
 * @param[in]   album      Album object
 *
 * @return                 sp_albumtype
 */
SP_LIBEXPORT(sp_albumtype) sp_album_type(sp_album *album);


/**
 * Increase the reference count of an album
 *
 * @param[in]   album       The album object
 */
SP_LIBEXPORT(void) sp_album_add_ref(sp_album *album);

/**
 * Decrease the reference count of an album
 *
 * @param[in]   album       The album object
 */
SP_LIBEXPORT(void) sp_album_release(sp_album *album);

/** @} */



/**
 * @defgroup artist Artist subsystem
 * @{
 */

/**
 * Return name of artist
 *
 * @param[in]   artist     Artist object
 *
 * @return                 Name of artist.
 *                         Returned string is valid as long as the artist object stays allocated
 *                         and no longer than the next call to sp_session_process_events()
 */
SP_LIBEXPORT(const char *) sp_artist_name(sp_artist *artist);

/**
 * Check if the artist object is populated with data
 *
 * @param[in]   artist     An artist object
 *
 * @return                 True if metadata is present, false if not
 *
 */
SP_LIBEXPORT(bool) sp_artist_is_loaded(sp_artist *artist);


/**
 * Increase the reference count of a artist
 *
 * @param[in]   artist       The artist object
 */
SP_LIBEXPORT(void) sp_artist_add_ref(sp_artist *artist);

/**
 * Decrease the reference count of a artist
 *
 * @param[in]   artist       The artist object
 */
SP_LIBEXPORT(void) sp_artist_release(sp_artist *artist);

/** @} */


/**
 * @defgroup albumbrowse Album browsing
 *
 * Browsing adds additional information to what an ::sp_album holds. It retrieves
 * copyrights, reviews and tracks of the album.
 *
 * @{
 */

/**
 * The type of a callback used in sp_albumbrowse_create()
 *
 * When the callback is called, the metadata of all tracks belonging to it will have
 * been loaded, so sp_track_is_loaded() will return non-zero. The ::sp_artist of the
 * album will also have been fully loaded.
 *
 * @param[in]   result          The same pointer returned by sp_albumbrowse_create()
 * @param[in]   userdata        The opaque pointer given to sp_albumbrowse_create()
 */
typedef void SP_CALLCONV albumbrowse_complete_cb(sp_albumbrowse *result, void *userdata);

/**
 * Initiate a request for browsing an album
 *
 * The user is responsible for freeing the returned album browse using sp_albumbrowse_release(). This can be done in the callback.
 *
 * Here is a snippet from \c browse.c:
 * @dontinclude browse.c
 * @skip sp_albumbrowse_create(session
 * @until }
 *
 * @param[in]   session         Session object
 * @param[in]   album           Album to be browsed. The album metadata does not have to be loaded
 * @param[in]   callback        Callback to be invoked when browsing has been completed. Pass NULL if you are not interested in this event.
 * @param[in]   userdata        Userdata passed to callback.
 *
 * @return                      Album browse object
 *
 * @see ::albumbrowse_complete_cb
 */
SP_LIBEXPORT(sp_albumbrowse *) sp_albumbrowse_create(sp_session *session, sp_album *album, albumbrowse_complete_cb *callback, void *userdata);

/**
 * Check if an album browse request is completed
 *
 * @param[in]   alb        Album browse object
 *
 * @return                 True if browsing is completed, false if not
 */
SP_LIBEXPORT(bool) sp_albumbrowse_is_loaded(sp_albumbrowse *alb);


/**
* Check if browsing returned an error code.
*
* @param[in]   alb        Album browse object
*
* @return                 Error code
*/
SP_LIBEXPORT(sp_error) sp_albumbrowse_error(sp_albumbrowse *alb);

/**
 * Given an album browse object, return the pointer to its album object
 *
 * @param[in]   alb        Album browse object
 *
 * @return                 Album object
 */
SP_LIBEXPORT(sp_album *) sp_albumbrowse_album(sp_albumbrowse *alb);

/**
 * Given an album browse object, return the pointer to its artist object
 *
 * @param[in]   alb        Album browse object
 *
 * @return                 Artist object
 */
SP_LIBEXPORT(sp_artist *) sp_albumbrowse_artist(sp_albumbrowse *alb);

/**
 * Given an album browse object, return number of copyright strings
 *
 * @param[in]   alb        Album browse object
 *
 * @return                 Number of copyright strings available, 0 if unknown
 */
SP_LIBEXPORT(int) sp_albumbrowse_num_copyrights(sp_albumbrowse *alb);

/**
 * Given an album browse object, return one of its copyright strings
 *
 * @param[in]   alb           Album browse object
 * @param[in]   index         The index for the copyright string. Should be in the interval [0, sp_albumbrowse_num_copyrights() - 1]
 *
 * @return                    Copyright string in UTF-8 format, or NULL if the index is invalid.
 *                            Returned string is valid as long as the album object stays allocated
 *                            and no longer than the next call to sp_session_process_events()
 */
SP_LIBEXPORT(const char *) sp_albumbrowse_copyright(sp_albumbrowse *alb, int index);

/**
 * Given an album browse object, return number of tracks
 *
 * @param[in]   alb         Album browse object
 *
 * @return                  Number of tracks on album
 */
SP_LIBEXPORT(int) sp_albumbrowse_num_tracks(sp_albumbrowse *alb);

/**
 * Given an album browse object, return a pointer to one of its tracks
 *
 * @param[in]   alb        Album browse object
 * @param[in]   index      The index for the track. Should be in the interval [0, sp_albumbrowse_num_tracks() - 1]
 *
 * @return                 A track.
 *
 * @see track
 */
SP_LIBEXPORT(sp_track *) sp_albumbrowse_track(sp_albumbrowse *alb, int index);

/**
 * Given an album browse object, return its review
 *
 * @param[in]   alb        Album browse object
 *
 * @return                 Review string in UTF-8 format.
 *                         Returned string is valid as long as the album object stays allocated
 *                         and no longer than the next call to sp_session_process_events()
 */
SP_LIBEXPORT(const char *) sp_albumbrowse_review(sp_albumbrowse *alb);


/**
 * Increase the reference count of an album browse result
 *
 * @param[in]   alb       The album browse result object
 */
SP_LIBEXPORT(void) sp_albumbrowse_add_ref(sp_albumbrowse *alb);

/**
 * Decrease the reference count of an album browse result
 *
 * @param[in]   alb       The album browse result object
 */
SP_LIBEXPORT(void) sp_albumbrowse_release(sp_albumbrowse *alb);

/** @} */


/**
 * @defgroup artistbrowse Artist browsing
 *
 * Artist browsing initiates the fetching of information for a certain artist.
 *
 * @note   There is currently no built-in functionality available for getting the albums belonging
 *         to an artist. For now, just iterate over all tracks and note the album to build a list of all albums.
 *         This feature will be added in a future version of the library.
 *
 * @{
 */

/**
 * The type of a callback used in sp_artistbrowse_create()
 *
 * When the callback is called, the metadata of all tracks belonging to it will have
 * been loaded, so sp_track_is_loaded() will return non-zero. The same goes for the
 * similar artist data.
 *
 * @param[in]   result          The same pointer returned by sp_artistbrowse_create()
 * @param[in]   userdata        The opaque pointer given to sp_artistbrowse_create()
 */
typedef void SP_CALLCONV artistbrowse_complete_cb(sp_artistbrowse *result, void *userdata);

/**
 * Initiate a request for browsing an artist
 *
 * The user is responsible for freeing the returned artist browse using sp_artistbrowse_release(). This can be done in the callback.
 *
 * Here is a snippet from \c browse.c:
 * @dontinclude browse.c
 * @skip sp_artistbrowse_create(session
 * @until }
 *
 * @param[in] session         Session object
 * @param[in] artist          Artist to be browsed. The artist metadata does not have to be loaded
 * @param[in] callback        Callback to be invoked when browsing has been completed. Pass NULL if you are not interested in this event.
 * @param[in] userdata        Userdata passed to callback.
 *
 * @return                    Artist browse object
 *
 * @see ::artistbrowse_complete_cb
 */
SP_LIBEXPORT(sp_artistbrowse *) sp_artistbrowse_create(sp_session *session, sp_artist *artist, artistbrowse_complete_cb *callback, void *userdata);

/**
 * Check if an artist browse request is completed
 *
 * @param[in]   arb        Artist browse object
 *
 * @return                 True if browsing is completed, false if not
 */
SP_LIBEXPORT(bool) sp_artistbrowse_is_loaded(sp_artistbrowse *arb);

/**
* Check if browsing returned an error code.
*
* @param[in]   arb        Artist browse object
*
* @return                 Error code
*/
SP_LIBEXPORT(sp_error) sp_artistbrowse_error(sp_artistbrowse *arb);

/**
 * Given an artist browse object, return a pointer to its artist object
 *
 * @param[in]   arb        Artist browse object
 *
 * @return                 Artist object
 */
SP_LIBEXPORT(sp_artist *) sp_artistbrowse_artist(sp_artistbrowse *arb);

/**
 * Given an artist browse object, return number of portraits available
 *
 * @param[in]   arb        Artist browse object
 *
 * @return                 Number of portraits for given artist
 */
SP_LIBEXPORT(int) sp_artistbrowse_num_portraits(sp_artistbrowse *arb);

/**
 * Return image ID representing a portrait of the artist
 *
 * @param[in] arb             Artist object
 * @param[in] index           The index of the portrait. Should be in the interval [0, sp_artistbrowse_num_portraits() - 1]
 *
 * @return                    ID byte sequence that can be passed to sp_image_create()
 *
 * @see sp_image_create
 */
SP_LIBEXPORT(const byte *) sp_artistbrowse_portrait(sp_artistbrowse *arb, int index);

/**
 * Given an artist browse object, return number of tracks
 *
 * @param[in] arb             Artist browse object
 *
 * @return                    Number of tracks for given artist
 */
SP_LIBEXPORT(int) sp_artistbrowse_num_tracks(sp_artistbrowse *arb);

/**
 * Given an artist browse object, return one of its tracks
 *
 * @param[in] arb             Album browse object
 * @param[in] index           The index for the track. Should be in the interval [0, sp_artistbrowse_num_tracks() - 1]
 *
 * @return                    A track object, or NULL if the index is out of range.
 *
 * @see track
 */
SP_LIBEXPORT(sp_track *) sp_artistbrowse_track(sp_artistbrowse *arb, int index);

/**
 * Given an artist browse object, return number of similar artists
 *
 * @param[in] arb             Artist browse object
 *
 * @return                    Number of similar artists for given artist
 */
SP_LIBEXPORT(int) sp_artistbrowse_num_similar_artists(sp_artistbrowse *arb);

/**
 * Given an artist browse object, return a similar artist by index
 *
 * @param[in] arb             Album browse object
 * @param[in] index           The index for the artist. Should be in the interval [0, sp_artistbrowse_num_similar_artists() - 1]
 *
 * @return                    A pointer to an artist object.
 *
 * @see artist
 */
SP_LIBEXPORT(sp_artist *) sp_artistbrowse_similar_artist(sp_artistbrowse *arb, int index);

/**
 * Given an artist browse object, return the artists biography
 *
 * @param[in] arb             Artist browse object
 *
 * @return                    Biography string in UTF-8 format.
 *                            Returned string is valid as long as the album object stays allocated
 *                            and no longer than the next call to sp_session_process_events()
 */
SP_LIBEXPORT(const char *) sp_artistbrowse_biography(sp_artistbrowse *arb);


/**
 * Increase the reference count of an artist browse result
 *
 * @param[in]   arb       The artist browse result object
 */
SP_LIBEXPORT(void) sp_artistbrowse_add_ref(sp_artistbrowse *arb);

/**
 * Decrease the reference count of an artist browse result
 *
 * @param[in]   arb       The artist browse result object
 */
SP_LIBEXPORT(void) sp_artistbrowse_release(sp_artistbrowse *arb);

/** @} */



/**
 * @defgroup image Image handling
 * @{
 */

/**
 * Image format
 */
typedef enum {
	SP_IMAGE_FORMAT_UNKNOWN = -1, ///< Unknown image format
	SP_IMAGE_FORMAT_RGB   = 0,    ///< 24 bit image in RGB form
	SP_IMAGE_FORMAT_BGR   = 1,    ///< 24 bit image in BGR form
	SP_IMAGE_FORMAT_RGBA  = 2,    ///< 32 bit image in RGBA form
	SP_IMAGE_FORMAT_RGBA_PRE= 3,  ///< 32 bit image in RGBA form with premultiplied alpha channel
	SP_IMAGE_FORMAT_BGRA  = 4,    ///< 32 bit image in BGRA form
	SP_IMAGE_FORMAT_BGRA_PRE= 5,  ///< 32 bit image in BGRA form with premultiplied alpha channel
} sp_imageformat;

/**
 * The type of a callback used to notify the application that an image
 * is done loading.
 */
typedef void SP_CALLCONV image_loaded_cb(sp_image *image, void *userdata);

/**
 * Create an image object
 *
 * Here is a snippet from \c track.c:
 * @dontinclude track.c
 * @skip sp_album_cover
 * @until }
 * @until }
 *
 * @param[in]  session    Session
 * @param[in]  image_id   Spotify image ID
 *
 * @return                Pointer to an image object. To free the object, use
 *                        sp_image_release()
 *
 * @see sp_album_cover
 * @see sp_artistbrowse_portrait
 */
SP_LIBEXPORT(sp_image *) sp_image_create(sp_session *session, const byte image_id[20]);

/**
 * Add a callback that will be invoked when the image is loaded
 *
 * If an image is loaded, and loading fails, the image will behave like an
 * empty image.
 *
 * Here is a snippet from \c track.c:
 * @dontinclude track.c
 * @skip g_image = sp_image_create
 * @until sp_image_add_load_callback
 *
 * @param[in]  image      Image object
 * @param[in]  callback   Callback that will be called when image has been
 *                        fetched.
 * @param[in]  userdata   Opaque pointer passed to \p callback
 *
 */
SP_LIBEXPORT(void) sp_image_add_load_callback(sp_image *image, image_loaded_cb *callback, void *userdata);

/**
 * Remove an image load callback previously added with sp_image_add_load_callback()
 *
 * @param[in]  image      Image object
 * @param[in]  callback   Callback that will not be called when image has been
 *                        fetched.
 * @param[in]  userdata   Opaque pointer passed to \p callback
 *
 */
SP_LIBEXPORT(void) sp_image_remove_load_callback(sp_image *image, image_loaded_cb *callback, void *userdata);

/**
 * Check if an image is loaded. Before the image is loaded, the rest of the
 * methods will behave as if the image is empty.
 *
 * @param[in]  image      Image object
 *
 * @return                True if image is loaded, false otherwise
 */
SP_LIBEXPORT(bool) sp_image_is_loaded(sp_image *image);

/**
* Check if image retrieval returned an error code.
*
* @param[in]   image      Image object
*
* @return                 Error code
*/
SP_LIBEXPORT(sp_error) sp_image_error(sp_image *image);

/**
 * Get image width
 *
 * @param[in]  image      Image object
 *
 * @return                Width of the image (in pixels)
 */
SP_LIBEXPORT(int) sp_image_width(sp_image *image);

/**
 * Get image height
 *
 * @param[in]  image      Image object
 *
 * @return                Height of the image (in pixels)
 */
SP_LIBEXPORT(int) sp_image_height(sp_image *image);

/**
 * Get image format
 *
 * @param[in]  image      Image object
 *
 * @return                Pixel format as described by sp_imageformat
 */
SP_LIBEXPORT(sp_imageformat) sp_image_format(sp_image *image);

/**
 * Lock pixels and return a pointer to the pixel data.
 *
 * You call sp_image_lock_pixels to obtain a pointer to the pixel buffer.
 * Then you call sp_image_unlock_pixels() when you are done. After you have
 * called sp_image_unlock_pixels() the pointer returned from sp_image_lock_pixels
 * is not valid anymore, and libspotify may move the image in memory or
 * delete it or compress it in any way it likes.
 *
 * Here is a snippet from \c track.c:
 * @dontinclude track.c
 * @skip sp_image_lock_pixels
 * @until sp_image_unlock_pixels
 *
 * @param[in]  image      Image object
 * @param[out] pitch      Offset in bytes between consecutive lines in pixel
 *                        data.
 *
 * @return                Pointer to pixels.
 */
SP_LIBEXPORT(void *) sp_image_lock_pixels(sp_image *image, int *pitch);

/**
 * Unlock pixels.
 *
 * After this call it is no longer safe to assume that the pointer returned by
 * sp_image_lock_pixels() is safe to dereference.
 *
 * @param[in]  image      Image object
 * @sa sp_image_lock_pixels
 *
 */
SP_LIBEXPORT(void) sp_image_unlock_pixels(sp_image *image);

/**
 * Get image ID
 *
 * @param[in]  image      Image object
 *
 * @return                Image ID
 */
SP_LIBEXPORT(const byte *) sp_image_image_id(sp_image *image);


/**
 * Increase the reference count of an image
 *
 * @param[in]   image     The image object
 */
SP_LIBEXPORT(void) sp_image_add_ref(sp_image *image);

/**
 * Decrease the reference count of an image
 *
 * @param[in]   image     The image object
 */
SP_LIBEXPORT(void) sp_image_release(sp_image *image);

/** @} */




/**
 * @defgroup search Search subsysten
 * @{
 */

/**
 * The type of a callback used in sp_search_create()
 *
 * When this callback is called, the sp_track_is_loaded(), sp_album_is_loaded(),
 * and sp_artist_is_loaded() functions will return non-zero for the objects
 * contained in the search result.
 *
 * @param[in]   result          The same pointer returned by sp_search_create()
 * @param[in]   userdata        The opaque pointer given to sp_search_create()
 */
typedef void SP_CALLCONV search_complete_cb(sp_search *result, void *userdata);

/**
 * Create a search object from the given query
 *
 * Here is a snippet from \c search.c:
 * @dontinclude search.c
 * @skip sp_search_create
 * @until }
 *
 * @param[in]  session    Session
 * @param[in]  query      Query search string, e.g. 'The Rolling Stones' or 'album:"The Black Album"'
 * @param[in]  track_offset     The offset among the tracks of the result
 * @param[in]  track_count      The number of tracks to ask for
 * @param[in]  album_offset     The offset among the albums of the result
 * @param[in]  album_count      The number of albums to ask for
 * @param[in]  artist_offset    The offset among the artists of the result
 * @param[in]  artist_count      The number of artists to ask for
 * @param[in]  callback   Callback that will be called once the search operation is complete. Pass NULL if you are not interested in this event.
 * @param[in]  userdata   Opaque pointer passed to \p callback
 *
 * @return                Pointer to a search object. To free the object, use sp_search_release()
 */
SP_LIBEXPORT(sp_search *) sp_search_create(sp_session *session, const char *query, int track_offset, int track_count, int album_offset, int album_count, int artist_offset, int artist_count, search_complete_cb *callback, void *userdata);

/**
 * Get load status for the specified search. Before it is loaded, it will behave as an empty search result.
 *
 * @param[in]  search   Search object
 *
 * @return              True if search is loaded, otherwise false
 */
SP_LIBEXPORT(bool) sp_search_is_loaded(sp_search *search);

/**
* Check if search returned an error code.
*
* @param[in]   search     Search object
*
* @return                 Error code
*/
SP_LIBEXPORT(sp_error) sp_search_error(sp_search *search);

/**
 * Get the number of tracks for the specified search
 *
 * @param[in]  search   Search object
 *
 * @return              The number of tracks for the specified search
 */
SP_LIBEXPORT(int) sp_search_num_tracks(sp_search *search);

/**
 * Return the track at the given index in the given search object
 *
 * @param[in]  search     Search object
 * @param[in]  index      Index of the wanted track. Should be in the interval [0, sp_search_num_tracks() - 1]
 *
 * @return                The track at the given index in the given search object
 */
SP_LIBEXPORT(sp_track *) sp_search_track(sp_search *search, int index);

/**
 * Get the number of albums for the specified search
 *
 * @param[in]  search   Search object
 *
 * @return              The number of albums for the specified search
 */
SP_LIBEXPORT(int) sp_search_num_albums(sp_search *search);

/**
 * Return the album at the given index in the given search object
 *
 * @param[in]  search     Search object
 * @param[in]  index      Index of the wanted album. Should be in the interval [0, sp_search_num_albums() - 1]
 *
 * @return                The album at the given index in the given search object
 */
SP_LIBEXPORT(sp_album *) sp_search_album(sp_search *search, int index);

/**
 * Get the number of artists for the specified search
 *
 * @param[in]  search   Search object
 *
 * @return              The number of artists for the specified search
 */
SP_LIBEXPORT(int) sp_search_num_artists(sp_search *search);

/**
 * Return the artist at the given index in the given search object
 *
 * @param[in]  search     Search object
 * @param[in]  index      Index of the wanted artist. Should be in the interval [0, sp_search_num_artists() - 1]
 *
 * @return                The artist at the given index in the given search object
 */
SP_LIBEXPORT(sp_artist *) sp_search_artist(sp_search *search, int index);

/**
 * Return the search query for the given search object
 *
 * @param[in]  search     Search object
 *
 * @return                The search query for the given search object
 */
SP_LIBEXPORT(const char *) sp_search_query(sp_search *search);

/**
 * Return the "Did you mean" query for the given search object
 *
 * @param[in]  search     Search object
 *
 * @return                The "Did you mean" query for the given search object, or the empty string if no such info is available
 */
SP_LIBEXPORT(const char *) sp_search_did_you_mean(sp_search *search);

/**
 * Return the total number of tracks for the search query - regardless of the interval requested at creation.
 * If this value is larger than the interval specified at creation of the search object, more search results are available.
 * To fetch these, create a new search object with a new interval.
 *
 * @param[in]  search     Search object
 *
 * @return                The total number of tracks matching the original query
 */
SP_LIBEXPORT(int) sp_search_total_tracks(sp_search *search);


/**
 * Increase the reference count of a search result
 *
 * @param[in]   search    The search result object
 */
SP_LIBEXPORT(void) sp_search_add_ref(sp_search *search);

/**
 * Decrease the reference count of a search result
 *
 * @param[in]   search    The search result object
 */
SP_LIBEXPORT(void) sp_search_release(sp_search *search);

/** @} */



/**
 * @defgroup playlist Playlist subsystem
 *
 * The playlist subsystem handles playlists and playlist containers (list of playlists).
 *
 * The playlist container functions are always valid, but your playlists are not
 * guaranteed to be loaded until the sp_session_callbacks#logged_in callback has
 * been issued.
 *
 * @{
 */

/**
 * Playlist callbacks
 *
 * Used to get notifications when playlists are updated.
 * If some callbacks should not be of interest, set them to NULL.
 */
typedef struct sp_playlist_callbacks {

	/**
	 * Called when one or more tracks have been added to a playlist
	 *
	 * @param[in]  pl         Playlist object
	 * @param[in]  tracks     Array of pointers to track objects
	 * @param[in]  num_tracks Number of entries in \p tracks
	 * @param[in]  position   Position in the playlist for the first track.
	 * @param[in]  userdata   Userdata passed to sp_playlist_add_callbacks()
	 */
	void (SP_CALLCONV *tracks_added)(sp_playlist *pl, const sp_track **tracks, int num_tracks, int position, void *userdata);

	/**
	 * Called when one or more tracks have been removed from a playlist
	 *
	 * @param[in]  pl         Playlist object
	 * @param[in]  tracks     Array of positions representing the tracks that were removed
	 * @param[in]  num_tracks Number of entries in \p tracks
	 * @param[in]  userdata   Userdata passed to sp_playlist_add_callbacks()
	 */
	void (SP_CALLCONV *tracks_removed)(sp_playlist *pl, const int *tracks, int num_tracks, void *userdata);

	/**
	 * Called when one or more tracks have been moved within a playlist
	 *
	 * @param[in]  pl         Playlist object
	 * @param[in]  tracks     Array of positions representing the tracks that were moved
	 * @param[in]  num_tracks Number of entries in \p tracks
	 * @param[in]  position   New position in the playlist for the first track.
	 * @param[in]  userdata   Userdata passed to sp_playlist_add_callbacks()
	 */
	void (SP_CALLCONV *tracks_moved)(sp_playlist *pl, const int *tracks, int num_tracks, int new_position, void *userdata);

	/**
	 * Called when a playlist has been renamed. sp_playlist_name() can be used to find out the new name
	 *
	 * @param[in]  pl         Playlist object
	 * @param[in]  userdata   Userdata passed to sp_playlist_add_callbacks()
	 */
	void (SP_CALLCONV *playlist_renamed)(sp_playlist *pl, void *userdata);

	/**
	 * Called when state changed for a playlist.
	 *
	 * The \em state in this case are the flags like collaborative or pending.
	 *
	 * @param[in]  pl         Playlist object
	 * @param[in]  userdata   Userdata passed to sp_playlist_add_callbacks()
	 */
	void (SP_CALLCONV *playlist_state_changed)(sp_playlist *pl, void *userdata);

	/**
	 * Called when a playlist is updating or is done updating
	 *
	 * This is called before and after a series of changes are applied to the
	 * playlist. It allows e.g. the user interface to defer updating until the
	 * entire operation is complete.
	 *
	 * @param[in]  pl         Playlist object
	 * @param[in]  done       True iff the update is completed
	 * @param[in]  userdata   Userdata passed to sp_playlist_add_callbacks()
	 */
	void (SP_CALLCONV *playlist_update_in_progress)(sp_playlist *pl, bool done, void *userdata);

	/**
	 * Called when metadata for one or more tracks in a playlist has been updated.
	 *
	 * @param[in]  pl         Playlist object
	 * @param[in]  userdata   Userdata passed to sp_playlist_add_callbacks()
	 */
	void (SP_CALLCONV *playlist_metadata_updated)(sp_playlist *pl, void *userdata);
} sp_playlist_callbacks;


/**
 * Get load status for the specified playlist
 *
 * @param[in]  playlist   Playlist object
 *
 * @return                True if playlist is loaded, otherwise false
 */
SP_LIBEXPORT(bool) sp_playlist_is_loaded(sp_playlist *playlist);

/**
 * Register interest in the given playlist
 *
 * Here is a snippet from \c jukebox.c:
 * @dontinclude jukebox.c
 * @skipline sp_playlist_add_callbacks
 *
 * @param[in]  playlist   Playlist object
 * @param[in]  callbacks  Callbacks, see #sp_playlist_callbacks
 * @param[in]  userdata   Userdata to be passed to callbacks
 * @sa sp_playlist_remove_callbacks
 *
 */
SP_LIBEXPORT(void) sp_playlist_add_callbacks(sp_playlist *playlist, sp_playlist_callbacks *callbacks, void *userdata);

/**
 * Unregister interest in the given playlist
 *
 * The combination of (\p callbacks, \p userdata) is used to find the entry to be removed
 *
 * Here is a snippet from \c jukebox.c:
 * @dontinclude jukebox.c
 * @skipline sp_playlist_remove_callbacks
 *
 * @param[in]  playlist   Playlist object
 * @param[in]  callbacks  Callbacks, see #sp_playlist_callbacks
 * @param[in]  userdata   Userdata to be passed to callbacks
 * @sa sp_playlist_add_callbacks
 *
 */
SP_LIBEXPORT(void) sp_playlist_remove_callbacks(sp_playlist *playlist, sp_playlist_callbacks *callbacks, void *userdata);

/**
 * Return number of tracks in the given playlist
 *
 * @param[in]  playlist   Playlist object
 *
 * @return                The number of tracks in the playlist
 */
SP_LIBEXPORT(int) sp_playlist_num_tracks(sp_playlist *playlist);

/**
 * Return the track at the given index in the given playlist
 *
 * @param[in]  playlist   Playlist object
 * @param[in]  index      Index into playlist container. Should be in the interval [0, sp_playlist_num_tracks() - 1]
 *
 * @return                The track at the given index
 */
SP_LIBEXPORT(sp_track *) sp_playlist_track(sp_playlist *playlist, int index);

/**
 * Return name of given playlist
 *
 * @param[in]  playlist   Playlist object
 *
 * @return                The name of the given playlist
 */
SP_LIBEXPORT(const char *) sp_playlist_name(sp_playlist *playlist);

/**
 * Rename the given playlist
 * The name must not consist of only spaces and it must be shorter than 256 characters.
 *
 * @param[in]  playlist   Playlist object
 * @param[in]  new_name   New name for playlist
 */
SP_LIBEXPORT(sp_error) sp_playlist_rename(sp_playlist *playlist, const char *new_name);

/**
 * Return a pointer to the user for the given playlist
 *
 * @param[in]  playlist   Playlist object
 *
 * @return                User object
 */
SP_LIBEXPORT(sp_user *) sp_playlist_owner(sp_playlist *playlist);

/**
 * Return collaborative status for a playlist.
 *
 * A playlist in collaborative state can be modifed by all users, not only the user owning the list
 *
 * @param[in]  playlist   Playlist object
 *
 * @return                true if playlist is collaborative, otherwise false
 */
SP_LIBEXPORT(bool) sp_playlist_is_collaborative(sp_playlist *playlist);

/**
 * Set collaborative status for a playlist.
 *
 * A playlist in collaborative state can be modifed by all users, not only the user owning the list
 *
 * @param[in]  playlist       Playlist object
 * @param[in]  collaborative  True or false
 *
 */
SP_LIBEXPORT(void) sp_playlist_set_collaborative(sp_playlist *playlist, bool collaborative);

/**
 * Check if a playlist has pending changes
 *
 * Pending changes are local changes that have not yet been acknowledged by the server.
 *
 * @param[in]  playlist       Playlist object
 *
 * @return                    A flag representing if there are pending changes or not
 */
SP_LIBEXPORT(bool) sp_playlist_has_pending_changes(sp_playlist *playlist);

/**
 * Add tracks to a playlist
 *
 * @param[in]  playlist       Playlist object
 * @param[in]  tracks         Array of pointer to tracks.
 * @param[in]  num_tracks     Length of \p tracks array
 * @param[in]  position       Start position in playlist where to insert the tracks
 *
 */
SP_LIBEXPORT(sp_error) sp_playlist_add_tracks(sp_playlist *playlist, const sp_track **tracks, int num_tracks, int position);

/**
 * Remove tracks from a playlist
 *
 * @param[in]  playlist       Playlist object
 * @param[in]  tracks         Array of pointer to track indices.
 *                            A certain track index should be present at most once, e.g. [0, 1, 2] is valid indata,
 *                            whereas [0, 1, 1] is invalid.
 * @param[in]  num_tracks     Length of \p tracks array
 *
 */
SP_LIBEXPORT(sp_error) sp_playlist_remove_tracks(sp_playlist *playlist, const int *tracks, int num_tracks);

/**
 * Move tracks in playlist
 *
 * @param[in]  playlist       Playlist object
 * @param[in]  tracks         Array of pointer to track indices to be moved.
 *                            A certain track index should be present at most once, e.g. [0, 1, 2] is valid indata,
 *                            whereas [0, 1, 1] is invalid.
 * @param[in]  num_tracks     Length of \p tracks array
 * @param[in]  new_position   New position for tracks
 *
 */
SP_LIBEXPORT(sp_error) sp_playlist_reorder_tracks(sp_playlist *playlist, const int *tracks, int num_tracks, int new_position);

/**
 * Playlist container callbacks.
 * If some callbacks should not be of interest, set them to NULL.
 *
 * @see sp_playlistcontainer_add_callbacks
 * @see sp_playlistcontainer_remove_callbacks
 */
typedef struct sp_playlistcontainer_callbacks {
	/**
	 * Called when a new playlist has been added to the playlist container.
	 *
	 * @param[in]  pc         Playlist container
	 * @param[in]  playlist   Playlist object.
	 * @param[in]  position   Position in list
	 * @param[in]  userdata   Userdata as set in sp_playlistcontainer_add_callbacks()
	 */
	void (SP_CALLCONV *playlist_added)(sp_playlistcontainer *pc, sp_playlist *playlist, int position, void *userdata);


	/**
	 * Called when a new playlist has been removed from playlist container
	 *
	 * @param[in]  pc         Playlist container
	 * @param[in]  playlist   Playlist object.
	 * @param[in]  position   Position in list
	 * @param[in]  userdata   Userdata as set in sp_playlistcontainer_add_callbacks()
	 */
	void (SP_CALLCONV *playlist_removed)(sp_playlistcontainer *pc, sp_playlist *playlist, int position, void *userdata);


	/**
	 * Called when a playlist has been moved in the playlist container
	 *
	 * @param[in]  pc         Playlist container
	 * @param[in]  playlist   Playlist object.
	 * @param[in]  position   Previous position in playlist container list
	 * @param[in]  new_position   New position in playlist container list
	 * @param[in]  userdata   Userdata as set in sp_playlistcontainer_add_callbacks()
	 */
	void (SP_CALLCONV *playlist_moved)(sp_playlistcontainer *pc, sp_playlist *playlist, int position, int new_position, void *userdata);
} sp_playlistcontainer_callbacks;


/**
 * Register interest in changes to a playlist container
 *
 * @param[in]  pc        Playlist container
 * @param[in]  callbacks Callbacks, see sp_playlistcontainer_callbacks
 * @param[in]  userdata  Opaque value passed to callbacks.
 *
 * @sa sp_session_playlistcontainer()
 * @sa sp_playlistcontainer_remove_callbacks
 */
SP_LIBEXPORT(void) sp_playlistcontainer_add_callbacks(sp_playlistcontainer *pc, sp_playlistcontainer_callbacks *callbacks, void *userdata);


/**
 * Unregister interest in changes to a playlist container
 *
 * @param[in]  pc        Playlist container
 * @param[in]  callbacks Callbacks, see sp_playlistcontainer_callbacks
 * @param[in]  userdata  Opaque value passed to callbacks.
 *
 * @sa sp_session_playlistcontainer()
 * @sa sp_playlistcontainer_add_callbacks
 */
SP_LIBEXPORT(void) sp_playlistcontainer_remove_callbacks(sp_playlistcontainer *pc, sp_playlistcontainer_callbacks *callbacks, void *userdata);

/**
 * Return the number of playlists in the given playlist container
 *
 * @param[in]  pc        Playlist container
 *
 * @return               Number of playlists, -1 if undefined
 *
 * @sa sp_session_playlistcontainer()
 */
SP_LIBEXPORT(int) sp_playlistcontainer_num_playlists(sp_playlistcontainer *pc);

/**
 * Return a pointer to the playlist at a specific index
 *
 * @param[in]  pc        Playlist container
 * @param[in]  index     Index in playlist container. Should be in the interval [0, sp_playlistcontainer_num_playlists() - 1]
 *
 * @return               Number of playlists.
 *
 * @sa sp_session_playlistcontainer()
 */
SP_LIBEXPORT(sp_playlist *) sp_playlistcontainer_playlist(sp_playlistcontainer *pc, int index);

/**
 * Add an empty playlist at the end of the playlist container.
 * The name must not consist of only spaces and it must be shorter than 256 characters.
 *
 * @param[in]  pc        Playlist container
 * @param[in]  name      Name of new playlist
 *
 * @return               Pointer to the new playlist. Can be NULL if the operation fails.
 */
SP_LIBEXPORT(sp_playlist *) sp_playlistcontainer_add_new_playlist(sp_playlistcontainer *pc, const char *name);

/**
 * Add an existing playlist at the end of the given playlist container
 *
 * @param[in]  pc        Playlist container
 * @param[in]  link      Link object pointing to a playlist
 *
 * @return               Pointer to the new playlist. Will be NULL if the playlist already exists.
 */
SP_LIBEXPORT(sp_playlist *) sp_playlistcontainer_add_playlist(sp_playlistcontainer *pc, sp_link *link);

/**
 * Remove playlist at index from the given playlist container
 *
 * @param[in]  pc        Playlist container
 * @param[in]  index     Index of playlist to be removed
 */
SP_LIBEXPORT(sp_error) sp_playlistcontainer_remove_playlist(sp_playlistcontainer *pc, int index);

/**
 * Move a playlist in the playlist container
 *
 * @param[in]  pc           Playlist container
 * @param[in]  index        Index of playlist to be moved
 * @param[in]  new_position New position for the playlist
 */
SP_LIBEXPORT(sp_error) sp_playlistcontainer_move_playlist(sp_playlistcontainer *pc, int index, int new_position);
/** @} */


/**
 * @defgroup user User handling
 * @{
 */

/**
 * Get a pointer to a string representing the user's canonical username.
 *
 * @param[in]   user         The Spotify user whose canonical username you would like a string representation of
 *
 * @return                   A string representing the canonical username.
 */
SP_LIBEXPORT(const char *) sp_user_canonical_name(sp_user *user);

/**
 * Get a pointer to a string representing the user's displayable username.
 * If there is no difference between the canonical username and the display name,
 * or if the library does not know about the display name yet, the canonical username will
 * be returned.
 *
 * @param[in]   user         The Spotify user whose displayable username you would like a string representation of
 *
 * @return                   A string
 */
SP_LIBEXPORT(const char *) sp_user_display_name(sp_user *user);

/**
 * Get load status for a user object. Before it is loaded, only the user's canonical username
 * is known.
 *
 * @param[in]   user         Spotify user object
 *
 * @return                   True if user object is loaded, otherwise false
 */
SP_LIBEXPORT(bool) sp_user_is_loaded(sp_user *user);

/** @} */

#ifdef __cplusplus
}
#endif

#endif /* PUBLIC_API_H */
/**
 * @example session.c
 *
 * The session.c example shows how you can use the session handling functions.
 */
/**
 * @example session_ready.c
 *
 * The session_ready.c example shows how you can use the session handling functions.
 */
/**
 * @example link.c
 *
 * The link.c example shows how you can use the link handling functions.
 */
/**
 * @example track.c
 *
 * The track.c example shows how you can use the track and image functions.
 */
/**
 * @example browse.c
 *
 * The browse.c example shows how you can use the album, artist, and browse functions.
 */
/**
 * @example search.c
 *
 * The search.c example shows how you can use search functions.
 */
/**
 * @example jukebox.c
 *
 * The jukebox.c example shows how you can use playback and playlist functions.
 */
