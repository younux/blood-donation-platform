/**
 * Created by younes.benhoumich on 27/11/2017.
 */

import {Author} from './author.model';


export class BaseComment {

  id: number;
  author: Author;
  parentId: number;
  content: string;
  timestamp: string;
  replyCount: number;

  constructor(id: number,
              author: Author,
              parentId: number,
              content: string,
              timestamp: string,
              replyCount?: number) {
    this.id = id;
    this.author = author;
    this.parentId = parentId;
    this.content = content;
    this.timestamp = timestamp;
    this.replyCount = replyCount || null;
  }

}

export class Comment extends BaseComment {
  replies: Array<BaseComment>;

  constructor(id: number,
              author: Author,
              parentId: number,
              content: string,
              timestamp: string,
              replyCount?: number,
              replies?: Array<BaseComment>) {
    super(id, author, parentId, content, timestamp, replyCount);
    this.replies = replies || null;
  }
}

