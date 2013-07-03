#include "libmockspotify.h"

// Playlist event
void
mocksp_event_playlist(event_type event, sp_playlist *p)
{
    if (!p->callbacks)
        return;

    sp_artist *artist = mocksp_artist_create("foo_", NULL, 1);
    sp_album *album = mocksp_album_create("bar_", artist, 2011, NULL, 0, 1, 1);
    sp_user *user = mocksp_user_create("foo", "", 0);
    sp_track *tracks[3] = {
        mocksp_track_create("foo", 1, &artist, album,
                            0, 0, 0, 0, 0, 1, 0, 0, 0, 0, NULL, 0, 0),
        mocksp_track_create("bar", 1, &artist, album,
                            0, 0, 0, 0, 0, 1, 0, 0, 0, 0, NULL, 0, 0),
        mocksp_track_create("baz", 1, &artist, album,
                            0, 0, 0, 0, 0, 1, 0, 0, 0, 0, NULL, 0, 0),
    };
    int nums[3] = { 0, 1, 2 };

    switch (event) {
    case MOCK_PLAYLIST_TRACKS_ADDED:
        if (p->callbacks->tracks_added)
            p->callbacks->tracks_added(p, tracks, 3, 0, p->userdata);
        break;
    case MOCK_PLAYLIST_TRACKS_MOVED:
        if (p->callbacks->tracks_moved)
            p->callbacks->tracks_moved(p, nums, 3, 0, p->userdata);
        break;
    case MOCK_PLAYLIST_TRACKS_REMOVED:
        if (p->callbacks->tracks_removed)
            p->callbacks->tracks_removed(p, nums, 3, p->userdata);
        break;

    case MOCK_PLAYLIST_RENAMED:
        if (p->callbacks->playlist_renamed)
            p->callbacks->playlist_renamed(p, p->userdata);
        break;

    case MOCK_PLAYLIST_STATE_CHANGED:
        if (p->callbacks->playlist_state_changed)
            p->callbacks->playlist_state_changed(p, p->userdata);
        break;

    case MOCK_PLAYLIST_UPDATE_IN_PROGRESS:
        if (p->callbacks->playlist_update_in_progress)
            p->callbacks->playlist_update_in_progress(p, 1, p->userdata);
        break;

    case MOCK_PLAYLIST_METADATA_UPDATED:
        if (p->callbacks->playlist_metadata_updated)
            p->callbacks->playlist_metadata_updated(p, p->userdata);
        break;

    case MOCK_PLAYLIST_TRACK_CREATED_CHANGED:
        if (p->callbacks->track_created_changed)
            p->callbacks->track_created_changed(p, 1, user, 123, p->userdata);
        break;

    case MOCK_PLAYLIST_TRACK_MESSAGE_CHANGED:
        if (p->callbacks->track_message_changed)
            p->callbacks->track_message_changed(p, 1, "foo", p->userdata);
        break;

    case MOCK_PLAYLIST_TRACK_SEEN_CHANGED:
        if (p->callbacks->track_seen_changed)
            p->callbacks->track_seen_changed(p, 1, 0, p->userdata);
        break;

    case MOCK_PLAYLIST_DESCRIPTION_CHANGED:
        if (p->callbacks->description_changed)
            p->callbacks->description_changed(p, "foo", p->userdata);
        break;

    case MOCK_PLAYLIST_SUBSCRIBERS_CHANGED:
        if (p->callbacks->subscribers_changed)
            p->callbacks->subscribers_changed(p, p->userdata);
        break;

    case MOCK_PLAYLIST_IMAGE_CHANGED:
        if (p->callbacks->image_changed)
            p->callbacks->image_changed(p, "01234567890123456789",
                                        p->userdata);
        break;

    default:
        break;
    }
}

// Container event
void
mocksp_event_playlistcontainer(event_type event, sp_playlistcontainer *c)
{
    if (!c->callbacks)
        return;

    sp_user *user = mocksp_user_create("user", "", 0);
    sp_playlist *playlist = mocksp_playlist_create("P", 1, user, 0, NULL, 0, 0,
                                                   0, NULL, 0, 0, 0, 0, NULL);

    switch (event) {
    case MOCK_CONTAINER_LOADED:
        if (c->callbacks->container_loaded)
            c->callbacks->container_loaded(c, c->userdata);
        break;
    case MOCK_CONTAINER_PLAYLIST_ADDED:
        if (c->callbacks->playlist_added)
            c->callbacks->playlist_added(c, playlist, 0, c->userdata);
        break;
    case MOCK_CONTAINER_PLAYLIST_MOVED:
        if (c->callbacks->playlist_moved)
            c->callbacks->playlist_moved(c, playlist, 0, 1, c->userdata);
        break;
    case MOCK_CONTAINER_PLAYLIST_REMOVED:
        if (c->callbacks->playlist_removed)
            c->callbacks->playlist_removed(c, playlist, 0, c->userdata);
        break;
    default:
        break;
    }
}
