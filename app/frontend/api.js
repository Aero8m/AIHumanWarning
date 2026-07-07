var API_BASE = '/api/v1';

async function request(method, path, data) {
    var url = API_BASE + path;
    var headers = { 'Content-Type': 'application/json' };
    var token = getToken();
    if (token) {
        headers['Authorization'] = 'Bearer ' + token;
    }
    var options = { method: method, headers: headers };
    if (data !== undefined && data !== null) {
        options.body = JSON.stringify(data);
    }
    var response = await fetch(url, options);
    var result = await response.json();
    if (result.code === 401) {
        clearToken();
        window.location.hash = 'page-auth';
        throw new Error(result.message);
    }
    if (result.code !== 200) {
        throw new Error(result.message || '请求失败');
    }
    return result.data;
}

var api = {
    register: function(username, password) {
        return request('POST', '/auth/register', { username: username, password: password });
    },
    login: function(username, password) {
        return request('POST', '/auth/login', { username: username, password: password });
    },
    changePassword: function(password) {
        return request('POST', '/auth/change_password', { password: password });
    },
    getStreams: function() {
        return request('GET', '/streams/');
    },
    addStream: function(data) {
        return request('POST', '/streams/add', data);
    },
    deleteStream: function(id) {
        return request('POST', '/streams/delete', { id: id });
    },
    editStream: function(data) {
        return request('POST', '/streams/edit', data);
    },
    getRecords: function(id) {
        return request('GET', '/streams/' + id + '/records');
    },
    getLiveStreamUrl: function(id) {
        return API_BASE + '/streams/' + id + '/live_stream?token=' + getToken();
    },
    getImageUrl: function(streamId, filename) {
        return API_BASE + '/streams/' + streamId + '/records/image/' + filename;
    },
    fetchImageBlob: function(streamId, filename) {
        var url = API_BASE + '/streams/' + streamId + '/records/image/' + filename;
        var token = getToken();
        return fetch(url, { headers: { 'Authorization': 'Bearer ' + token } }).then(function(r) {
            if (!r.ok) throw new Error('load image failed');
            return r.blob();
        });
    },
    getLlmConfig: function() {
        return request('GET', '/llm_info/');
    },
    editLlmConfig: function(data) {
        return request('POST', '/llm_info/edit', data);
    }
};
